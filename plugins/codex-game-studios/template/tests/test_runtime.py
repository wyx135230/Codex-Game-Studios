import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import tomllib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('studio', ROOT / 'scripts/studio.py')
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.mock = patch.object(studio, 'ROOT', self.root)
        self.mock.start(); self.addCleanup(self.mock.stop)

    def test_multifile_add_update_delete(self):
        (self.root / 'old.txt').write_text('one\ntwo\nthree\n')
        (self.root / 'gone.txt').write_text('gone\n')
        result = studio.patch_files('*** Begin Patch\n*** Add File: new.txt\n+你好\n*** Update File: old.txt\n@@\n one\n-two\n+changed\n three\n*** Delete File: gone.txt\n*** End Patch\n')
        self.assertEqual([x['content'] for x in result], ['你好\n', 'one\nchanged\nthree\n', ''])
        self.assertEqual((self.root / 'old.txt').read_text(), 'one\ntwo\nthree\n')

    def test_move_checks_source_and_destination(self):
        (self.root / 'old').write_text('before\n')
        result = studio.patch_files('*** Begin Patch\n*** Update File: old\n*** Move to: new\n@@\n-before\n+after\n*** End Patch\n')
        self.assertEqual([Path(x['file_path']).name for x in result], ['new', 'old'])
        self.assertEqual([x['content'] for x in result], ['after\n', ''])

    def test_reject_escape(self):
        for path in ('../outside', str(self.root.parent / 'outside')):
            with self.assertRaises(ValueError):
                studio.patch_files(f'*** Begin Patch\n*** Add File: {path}\n+x\n*** End Patch\n')

    def test_reject_symlink_escape(self):
        try:
            (self.root / 'link').symlink_to(self.root.parent, target_is_directory=True)
        except OSError:
            self.skipTest('symlink creation unavailable')
        with self.assertRaises(ValueError):
            studio.patch_files('*** Begin Patch\n*** Add File: link/outside\n+x\n*** End Patch\n')

    def test_invalid_patch_fails(self):
        for content in ('oops', '*** Begin Patch\n*** Add File: x\n+x\n'):
            with self.assertRaises(ValueError):
                studio.patch_files(content)

    def test_post_reads_actual_content(self):
        (self.root / 'x').write_text('actual\n')
        result = studio.patch_files('*** Begin Patch\n*** Add File: x\n+original\n*** End Patch\n', post=True)
        self.assertEqual(result[0]['content'], 'actual\n')

    def test_hunk_anchor_selects_correct_duplicate_context(self):
        (self.root / 'x').write_text('def first():\n    return 1\ndef second():\n    return 1\n')
        result = studio.patch_files('*** Begin Patch\n*** Update File: x\n@@ def second():\n-    return 1\n+    return 2\n*** End Patch\n')
        self.assertEqual(result[0]['content'], 'def first():\n    return 1\ndef second():\n    return 2\n')


class HookTests(unittest.TestCase):
    def test_cli_denial_uses_native_json(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/studio.py'), 'hook', 'PreToolUse'],
            input=json.dumps({'tool_name': 'exec_command', 'tool_input': {'cmd': 'git reset --hard HEAD'}}),
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_cli_post_failure_uses_native_feedback(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/studio.py'), 'hook', 'PostToolUse'],
            input=json.dumps({'tool_name': 'apply_patch', 'tool_input': {'command': 'malformed'}}),
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['decision'], 'block')
    def test_shell_policy(self):
        for cmd in ('git reset --hard HEAD', 'git push --force origin main', 'rm -rf src'):
            with self.assertRaises(ValueError):
                studio.policy('Bash', {'command': cmd})
        studio.policy('Bash', {'command': 'git status --short'})

    def test_sensitive_files(self):
        for tool, name in [('Read', '.env.local'), ('Write', 'Content/Map.umap')]:
            with self.assertRaises(ValueError):
                studio.policy(tool, {'file_path': name})

    def test_exec_command_normalized_and_denial_forwarded(self):
        calls = []
        def run(script, args=(), payload=None, timeout=60):
            calls.append((script, payload))
            return subprocess.CompletedProcess([], 2, '', 'review receipt missing')
        with patch.object(studio, 'shell', side_effect=run):
            with self.assertRaisesRegex(ValueError, 'review receipt missing'):
                studio.hook('PreToolUse', {'tool_name': 'exec_command', 'tool_input': {'cmd': 'git commit -m test'}})
        self.assertEqual(calls[0][1]['tool_name'], 'Bash')
        self.assertEqual(calls[0][1]['tool_input']['command'], 'git commit -m test')

    def test_all_patch_files_validated(self):
        calls = []
        def run(script, args=(), payload=None, timeout=60):
            calls.append(payload['tool_input']['file_path'])
            return subprocess.CompletedProcess([], 0, '', '')
        with patch.object(studio, 'shell', side_effect=run):
            studio.hook('PreToolUse', {'tool_name': 'apply_patch', 'tool_input': {'command':
                        '*** Begin Patch\n*** Add File: a.txt\n+a\n*** Add File: b.txt\n+b\n*** End Patch\n'}})
        self.assertEqual({Path(p).name for p in calls}, {'a.txt', 'b.txt'})
        self.assertEqual(len(calls), 4)  # registry and write guard per file

    def test_context_forwarded(self):
        result = subprocess.CompletedProcess([], 0, json.dumps({'hookSpecificOutput': {'additionalContext': 'warning'}}), '')
        with patch.object(studio, 'shell', return_value=result):
            obj = studio.hook('PostToolUse', {'tool_name': 'Write', 'tool_input': {'file_path': 'x'}})
        self.assertIn('warning', obj['hookSpecificOutput']['additionalContext'])


class InventoryTests(unittest.TestCase):
    def test_all_source_files_accounted_for(self):
        manifest = json.loads((ROOT / 'docs/migration-manifest.json').read_text())
        self.assertEqual(len(manifest), 638)
        for entry in manifest:
            self.assertTrue((ROOT / entry['target']).is_file(), entry['target'])

    def test_native_roles_match_all_original_roles(self):
        originals = {f.stem for f in (ROOT / '.codex/agents').glob('*.md')}
        native = {f.stem for f in (ROOT / '.codex/agents').glob('*.toml')}
        self.assertEqual(len(native), 49)
        self.assertEqual(originals, native)
        for role in native:
            obj = tomllib.loads((ROOT / f'.codex/agents/{role}.toml').read_text(encoding='utf-8'))
            self.assertEqual(obj['name'], role)
            body = (ROOT / f'.codex/agents/{role}.md').read_text(encoding='utf-8').split('---', 2)[2].lstrip()
            self.assertIn(body, obj['developer_instructions'])
            self.assertNotIn('model', obj)

    def test_native_skills_have_no_implicit_shell_injection(self):
        skills = list((ROOT / '.agents/skills').glob('*/SKILL.md'))
        self.assertEqual(len(skills), 74)
        for file in skills:
            text = file.read_text(encoding='utf-8')
            self.assertNotRegex(text, r'(?m)^!`')
            self.assertNotIn('STUDIO_SKILL_DIR', text)
            front = text.split('---', 2)[1]
            self.assertIn('name: ' + file.parent.name, front)
            self.assertIn('description:', front)
            self.assertNotIn('model:', front)

    def test_hooks_are_native_supported_events(self):
        if (ROOT / '.studio/installation.json').exists():
            self.assertFalse((ROOT / '.codex/hooks.json').exists(), 'plugin mode must not register project hooks twice')
            return
        hooks = json.loads((ROOT / '.codex/hooks.json').read_text())['hooks']
        self.assertEqual(set(hooks), {'SessionStart', 'PreToolUse', 'PostToolUse', 'PermissionRequest',
                                     'PreCompact', 'Stop', 'SubagentStart', 'SubagentStop'})
        for event, groups in hooks.items():
            cmd = groups[0]['hooks'][0]
            self.assertIn('studio.py', cmd['command'])
            self.assertIn(event, cmd['commandWindows'])


if __name__ == '__main__':
    unittest.main()
