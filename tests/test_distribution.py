import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_plugin import NAME, VERSION
from validate_distribution import validate_plugin, validate_marketplace


class DistributionTests(unittest.TestCase):
    def test_native_plugin_is_complete(self):
        result = validate_plugin(ROOT / 'dist' / f'{NAME}-{VERSION}.zip')
        self.assertEqual(result['skills'], 75)
        self.assertEqual(result['source_files'], 638)

    def test_marketplace_matches_upload_package(self):
        result = validate_marketplace(ROOT / 'dist/codex-game-studios-marketplace',
                                      ROOT / 'dist' / f'{NAME}-{VERSION}.zip')
        self.assertEqual(result['source'], './plugins/codex-game-studios')

    def test_marketplace_zip_is_rejected_as_plugin_upload(self):
        with self.assertRaisesRegex(ValueError, 'manifest at root'):
            validate_plugin(ROOT / 'dist' / f'{NAME}-marketplace-{VERSION}.zip')

    def test_missing_icon_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / 'broken.zip'
            with zipfile.ZipFile(ROOT / 'dist' / f'{NAME}-{VERSION}.zip') as src, zipfile.ZipFile(broken, 'w') as out:
                for name in src.namelist():
                    if name != 'assets/icon.svg':
                        out.writestr(name, src.read(name))
            with self.assertRaisesRegex(ValueError, 'component'):
                validate_plugin(broken)


if __name__ == '__main__':
    unittest.main()
