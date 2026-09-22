"""验证锁文件检查不会放过第三方版本漂移。"""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("sync_lock", Path(__file__).with_name("sync-lock.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

LOCK = '''[[package]]
name = "local"
version = "0.0.0"
[[package]]
name = "rama-error"
version = "0.3.0-alpha.4"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "original"
'''


class LockTests(unittest.TestCase):
    def test_local_version_change_allowed(self):
        self.assertEqual(module.external_packages(LOCK), module.external_packages(LOCK.replace('0.0.0', '0.155.1')))

    def test_external_version_change_detected(self):
        self.assertNotEqual(module.external_packages(LOCK), module.external_packages(LOCK.replace('0.3.0-alpha.4', '0.3.0')))

    def test_checksum_change_detected(self):
        self.assertNotEqual(module.external_packages(LOCK), module.external_packages(LOCK.replace('original', 'changed')))


if __name__ == '__main__':
    unittest.main()
