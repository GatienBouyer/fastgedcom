import unittest

from fastgedcom.helpers import extract_name_parts


class TestParser(unittest.TestCase):
	def test_extract_name_parts(self) -> None:
		self.assertEqual(extract_name_parts("Gatien /BOUYER/"), ("Gatien", "BOUYER"))
		self.assertEqual(extract_name_parts(" /BOUYER/"), ("", "BOUYER"))
		self.assertEqual(extract_name_parts("Gatien "), ("Gatien", ""))
		self.assertEqual(extract_name_parts("Gatien //"), ("Gatien", ""))
		self.assertEqual(extract_name_parts("Gatien ... /BOUYER / ***"), ("Gatien ... ***", "BOUYER"))


if __name__ == '__main__':
	unittest.main()
