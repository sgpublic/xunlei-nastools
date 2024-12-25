import unittest
from typing import Tuple, List


class MyTestCase(unittest.TestCase):
    def test_version(self):
        self.assertFalse(self._check_version_at_lest("3.11.2", "3.21.0"))
        self.assertTrue(self._check_version_at_lest("3.21.0", "3.21.0"))
        self.assertTrue(self._check_version_at_lest("3.21.2", "3.21.0"))

    @staticmethod
    def _check_version_at_lest(current_version: str, target_version: str) -> bool:
        if current_version == target_version:
            return True
        current_vers, current_n = MyTestCase._parse_version(current_version)
        target_vers, target_n = MyTestCase._parse_version(target_version)
        index = 0
        while index < current_n and index < target_n:
            if current_vers[index] < target_vers[index]:
                return False
            if current_vers[index] > target_vers[index]:
                return True
            index += 1
        return current_n >= target_n

    @staticmethod
    def _parse_version(version_name: str) -> Tuple[List[int], int]:
        vers = [int(x) for x in version_name.split('.')]
        return vers, len(vers)

if __name__ == '__main__':
    unittest.main()
