"""Integration checks for a relocated, extracted plugin and a minimal game workspace."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_plugin import NAME, VERSION
from plugin_workspace import cleanup, initialize


class ResourceWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='studio resources spaces ')
        cls.base = Path(cls.temp.name)
        cls.package = cls.base / 'installed plugin'
        with zipfile.ZipFile(ROOT / 'dist' / f'{NAME}-{VERSION}.zip') as archive:
            archive.extractall(cls.package)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_helper(self, game, *args):
        return subprocess.run([sys.executable, str(self.package / 'scripts/studio.py'), *args],
                              cwd=game, env=dict(os.environ, PYTHONUTF8='1'), capture_output=True,
                              text=True, encoding='utf-8', errors='replace', timeout=90)

    def test_relocated_plugin_runs_helpers_without_copying_or_mutating_framework(self):
        game = self.base / 'my game'
        initialize(game, self.package / 'framework')
        before = {p.relative_to(self.package).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.package.rglob('*') if p.is_file()}
        for command, expected in [
            (('doctor',), '"agents": 49'),
            (('run', 'config-set.sh', 'modes.rigor', 'standard'), 'standard'),
            (('helper', '.codex/hooks/yaml-helper.sh', 'resolve_config'), 'standard'),
            (('run', 'project-state.sh'), 'my game'),
            (('run', 'skill-lint.sh', 'all'), 'checked\t75 of 75'),
            (('run', 'agent-check.sh'), 'AGENTS: 49'),
            (('run', 'artifact-check.sh'), 'ROOT:'),
        ]:
            with self.subTest(command=command):
                result = self.run_helper(game, *command)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(expected, result.stdout)
        after = {p.relative_to(self.package).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.package.rglob('*') if p.is_file()}
        self.assertEqual(before, after, 'a helper modified installed plugin resources')
        self.assertFalse((game / '.agents').exists())
        self.assertFalse((game / '.codex').exists())
        self.assertFalse((game / 'scripts').exists())
        self.assertIn('standard', (game / 'project.yaml').read_text(encoding='utf-8'))

    def test_packaged_shell_scripts_are_valid_bash(self):
        spec = importlib.util.spec_from_file_location('packaged_studio', self.package / 'scripts/studio.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for file in (self.package / 'framework/.codex').rglob('*.sh'):
            with self.subTest(file=file.name):
                result = subprocess.run([module.bash_path(), '-n', str(file)], capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_packaged_native_hook_denies_command_from_nested_workspace(self):
        game = self.base / 'hook game'
        initialize(game, self.package / 'framework')
        nested = game / 'src'
        nested.mkdir()
        payload = {'cwd': str(nested), 'tool_name': 'exec_command', 'tool_input': {'cmd': 'git reset --hard HEAD'}}
        result = subprocess.run([sys.executable, str(self.package / 'scripts/plugin_hook.py'), 'PreToolUse'],
                                input=json.dumps(payload), cwd=nested, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertFalse((game / '.codex').exists())

    def test_runpy_hook_entry_rebinds_without_import_path_or_cache_writes(self):
        game = self.base / 'runpy game'
        initialize(game, self.package / 'framework')
        payload = {'cwd': str(game), 'tool_name': 'exec_command', 'tool_input': {'cmd': 'git reset --hard HEAD'}}
        before = {p.relative_to(self.package).as_posix() for p in self.package.rglob('*') if p.is_file()}
        code = 'import runpy,sys; sys.argv=[sys.argv[1], "PreToolUse"]; runpy.run_path(sys.argv[0], run_name="__main__")'
        result = subprocess.run([sys.executable, '-c', code, str(self.package / 'scripts/plugin_hook.py')],
                                cwd=game, input=json.dumps(payload), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(before, {p.relative_to(self.package).as_posix() for p in self.package.rglob('*') if p.is_file()})

    def test_full_skill_body_and_references_live_only_in_plugin(self):
        text = (self.package / 'skills/prototype/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Phase 1', text)
        self.assertIn('references/1-question.md', text)
        self.assertTrue((self.package / 'skills/prototype/references/1-question.md').is_file())
        self.assertFalse((self.package / 'framework/.agents/skills').exists())
        self.assertFalse((self.package / 'template').exists())


class LegacyCleanupTests(unittest.TestCase):
    def test_cleanup_removes_only_unchanged_owned_framework_and_keeps_game_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {'.agents/skills/start/SKILL.md': 'workflow', '.codex/rules/gameplay.md': 'rules',
                     'src/player.gd': 'game code', '.codex/agent-memory/role/MEMORY.md': 'memory'}
            hashes = {}
            for rel, data in files.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(data)
                hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
            (root / '.codex/rules/gameplay.md').write_text('user customized rules')
            (root / '.studio').mkdir()
            (root / '.studio/installation.json').write_text(json.dumps({'plugin': NAME, 'files': hashes}))
            preview = cleanup(root)
            self.assertEqual(preview['files'], ['.agents/skills/start/SKILL.md'])
            self.assertTrue((root / preview['files'][0]).exists())
            cleanup(root, apply=True)
            self.assertFalse((root / '.agents').exists())
            self.assertEqual((root / '.codex/rules/gameplay.md').read_text(), 'user customized rules')
            self.assertEqual((root / 'src/player.gd').read_text(), 'game code')
            self.assertEqual((root / '.codex/agent-memory/role/MEMORY.md').read_text(), 'memory')

    def test_override_instructions_receive_bridge_and_survive_rebinding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'game'
            root.mkdir()
            framework = Path(tmp) / 'plugin/framework'
            framework.mkdir(parents=True)
            (framework / 'project.yaml').write_text('schema_version: 1\n')
            (root / 'AGENTS.md').write_text('base rules')
            (root / 'AGENTS.override.md').write_text('override rules')
            initialize(root, framework)
            self.assertEqual((root / 'AGENTS.md').read_text(), 'base rules')
            self.assertIn('codex-game-studios:begin', (root / 'AGENTS.override.md').read_text())
            self.assertEqual(len(list(root.glob('AGENTS*'))), 2)


if __name__ == '__main__':
    unittest.main()
