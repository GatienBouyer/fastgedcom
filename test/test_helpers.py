import unittest

from fastgedcom.base import TrueLine
from fastgedcom.helpers import (extract_name_parts, format_name,
                                get_all_sub_lines, get_source)
from fastgedcom.parser import parse


class TestHelpers(unittest.TestCase):
	def test_format_name(self) -> None:
		self.assertEqual(format_name("Gatien /BOUYER/"), "Gatien BOUYER")
		self.assertEqual(format_name(" /BOUYER/"), " BOUYER")
		self.assertEqual(format_name("Gatien "), "Gatien ")
		self.assertEqual(format_name("Gatien //"), "Gatien ")

	def test_extract_name_parts(self) -> None:
		self.assertEqual(extract_name_parts("Gatien /BOUYER/"), ("Gatien", "BOUYER"))
		self.assertEqual(extract_name_parts(" /BOUYER/"), ("", "BOUYER"))
		self.assertEqual(extract_name_parts("Gatien "), ("Gatien", ""))
		self.assertEqual(extract_name_parts("Gatien //"), ("Gatien", ""))
		self.assertEqual(extract_name_parts("Gatien ... /BOUYER / ***"), ("Gatien ... ***", "BOUYER"))

	def test_sub_rec_recursive(self) -> None:
		surn = TrueLine(2, "SURN", "BOUYER", [])
		givn = TrueLine(2, "GIVN", "Gatien", [])
		name = TrueLine(1, "NAME", "Gatien /BOUYER/", [surn, givn])
		sex = TrueLine(1, "SEX", "M", [])
		indi = TrueLine(0, "@I1@", "INDI", [name, sex])
		all_recs = list(get_all_sub_lines(indi))
		self.assertListEqual(all_recs, [name, surn, givn, sex])

	def test_get_source(self) -> None:
		header = "0 HEAD\n1 GEDC\n2 VERS 5.5\n2 FORM LINEAGE-LINKED\n1 CHAR UTF-8\n"
		doc, _ = parse(header.splitlines())
		self.assertEqual(get_source(doc["HEAD"]), header)
		self.assertEqual(get_source(doc["@@"]), "")


if __name__ == '__main__':
	unittest.main()
