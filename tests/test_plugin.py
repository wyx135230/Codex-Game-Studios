import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


manager = module('plugin_manager')
workspace = module('plugin_workspace')


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.home = self.base / 'home'
        self.source = self.base / 'package'
        self.source.mkdir()
        (self.source / 'plugin.json').write_text(json.dumps({'name': manager.NAME, 'version': '0.1.0'}))

    def test_roundtrip_preserves_other_plugin_config_and_game_data(self):
        market = self.home / '.agents/plugins/marketplace.json'
        market.parent.mkdir(parents=True)
        other = {'name': 'other', 'source': {'source': 'local', 'path': './other'}}
        market.write_text(json.dumps({'name': 'my-market', 'plugins': [other]}))
        config = self.home / '.codex/config.toml'
        config.parent.mkdir(parents=True)
        original = '# user settings\nmodel = "chosen-model"\n[plugins."other@my-market"]\nenabled = true\n'
        config.write_text(original)
        game = self.home / 'games/my-game'
        game.mkdir(parents=True)
        (game / 'source.cs').write_text('important game source')
        first = manager.install(self.home, self.source)
        self.assertEqual(first['status'], 'installed')
        self.assertEqual(manager.install(self.home, self.source)['status'], 'already-installed')
        self.assertEqual(json.loads(market.read_text())['name'], 'my-market')
        self.assertEqual(manager.uninstall(self.home)['status'], 'uninstalled')
        self.assertEqual(config.read_text(), original)
        self.assertEqual(json.loads(market.read_text())['plugins'], [other])
        self.assertEqual((game / 'source.cs').read_text(), 'important game source')
        self.assertEqual(manager.uninstall(self.home)['status'], 'not-installed')

    def test_refuse_unowned_directory(self):
        _, target, _ = manager.locations(self.home)
        target.mkdir(parents=True)
        (target / 'keep').write_text('keep')
        with self.assertRaises(ValueError):
            manager.install(self.home, self.source)
        self.assertTrue((target / 'keep').exists())

    def test_modified_config_uninstall_has_no_partial_mutation(self):
        manager.install(self.home, self.source)
        config = self.home / '.codex/config.toml'
        config.write_text(config.read_text().replace('enabled = true', 'enabled = false'))
        market = self.home / '.agents/plugins/marketplace.json'
        before = market.read_text()
        with self.assertRaisesRegex(ValueError, 'modified'):
            manager.uninstall(self.home)
        self.assertEqual(market.read_text(), before)

    def test_existing_name_conflict_preserved(self):
        market = self.home / '.agents/plugins/marketplace.json'
        market.parent.mkdir(parents=True)
        market.write_text(json.dumps({'name': 'local', 'plugins': [{'name': manager.NAME}]}))
        with self.assertRaises(ValueError):
            manager.install(self.home, self.source)

    def test_uninstall_after_native_config_reserialization(self):
        manager.install(self.home, self.source)
        config = self.home / '.codex/config.toml'
        config.write_text('model = "keep"\n\n[plugins."codex-game-studios@local-game-studios"]\nenabled=true\n\n[other]\nvalue = 3\n')
        self.assertEqual(manager.uninstall(self.home)['status'], 'uninstalled')
        text = config.read_text()
        self.assertIn('model = "keep"', text)
        self.assertIn('[other]', text)
        self.assertNotIn('[plugins.', text)


class WorkspaceTests(unittest.TestCase):
    def test_setup_keeps_framework_in_plugin_and_creates_only_three_project_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            template = base / 'framework'
            (template / '.agents/skills/start').mkdir(parents=True)
            (template / '.agents/skills/start/SKILL.md').write_text('workflow')
            (template / 'AGENTS.md').write_text('long framework contract')
            (template / 'project.yaml').write_text('schema_version: 1\n')
            root = base / 'game'
            workspace.initialize(root, template)
            files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(files, {'AGENTS.md', 'project.yaml', '.studio/installation.json'})
            self.assertIn('codex-game-studios', (root / 'AGENTS.md').read_text())

    def test_setup_adds_small_managed_bridge_to_existing_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            template = base / 'framework'
            template.mkdir()
            (template / 'project.yaml').write_text('schema_version: 1\n')
            root = base / 'game'
            root.mkdir()
            original = b'# My project\r\nKeep my rules.\r\n'
            (root / 'AGENTS.md').write_bytes(original)
            workspace.initialize(root, template)
            first = (root / 'AGENTS.md').read_bytes()
            workspace.initialize(root, template)
            self.assertTrue(first.startswith(original))
            self.assertIn(b'<!-- codex-game-studios:begin -->', first)
            self.assertEqual(first, (root / 'AGENTS.md').read_bytes())

    def test_initialize_idempotent_and_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            template = base / 'template'
            (template / '.codex').mkdir(parents=True)
            (template / 'AGENTS.md').write_text('studio instructions')
            (template / 'project.yaml').write_text('template settings')
            (template / '.codex/hooks.json').write_text('{}')
            root = base / 'game'
            root.mkdir()
            (root / 'AGENTS.md').write_text('my instructions')
            (root / 'project.yaml').write_text('my engine settings')
            first = workspace.initialize(root, template)
            second = workspace.initialize(root, template)
            self.assertTrue((root / 'AGENTS.md').read_text().startswith('my instructions'))
            self.assertEqual((root / 'project.yaml').read_text(), 'my engine settings')
            self.assertFalse((root / 'STUDIO.md').exists())
            self.assertFalse((root / '.codex/hooks.json').exists())
            self.assertEqual(second['created'], [])
            self.assertIn('project.yaml', first['preserved'])
            self.assertTrue((root / '.studio/installation.json').is_file())

    def test_cannot_initialize_inside_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                workspace.initialize(Path(tmp) / 'bad', Path(tmp))

    def test_preserve_foreign_workspace_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            template = base / 'template'
            template.mkdir()
            root = base / 'game'
            (root / '.studio').mkdir(parents=True)
            ledger = root / '.studio/installation.json'
            original = '{"plugin":"other","files":{}}'
            ledger.write_text(original)
            with self.assertRaisesRegex(ValueError, 'another installation'):
                workspace.initialize(root, template)
            self.assertEqual(ledger.read_text(), original)


if __name__ == '__main__':
    unittest.main()
