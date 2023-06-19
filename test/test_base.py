import unittest

from fastgedcom.parser import strict_parse
from fastgedcom.base import TrueLine
from pathlib import Path

gedcom_file = Path(__file__).parent / "test_data" / "relatives.ged"

class TestBase(unittest.TestCase):
	def test_syntactic_sugar(self) -> None:
		doc = strict_parse(gedcom_file)
		self.assertTrue(doc["@I1@"])
		self.assertFalse(doc["@I99@"])
		self.assertTrue("@I1@" in doc)
		self.assertFalse("@I99@" in doc)
		self.assertTrue(doc["@I1@"] > "NAME")
		self.assertFalse((doc["@I1@"] > "NAME") > "_ALIA")
		self.assertFalse((doc["@I1@"] > "DEAT") > "DATE")
		self.assertEqual((doc["@I1@"] > "NAME") >= "GIVN", "root")
		self.assertEqual((doc["@I1@"] > "DEAT") >= "DATE", "")
		self.assertListEqual(list(doc >> ""), [doc["HEAD"], doc["TRLR"]])
		self.assertListEqual(list(doc["@F3@"] >> "CHIL"), [
			TrueLine(1, "CHIL", "@I7@"), TrueLine(1, "CHIL", "@I41@")
		])
		self.assertListEqual(list(doc["@F99@"] >> "CHIL"), [])

	def test_payload_with_cont(self) -> None:
		note_text1 = "This is a text\non several\nlines"
		note_line1 = TrueLine(1, "NOTE", "This is a text", [
			TrueLine(1, "CONT", "on several"),
			TrueLine(1, "CONT", "lines"),
		])
		self.assertEqual(note_line1.payload_with_cont, note_text1)
		note_text2 = "This is a very long text that is split"
		note_line2 = TrueLine(1, "NOTE", "This is a very", [
			TrueLine(1, "CONC", "long text"),
			TrueLine(1, "CONC", "that is split"),
		])
		self.assertEqual(note_line2.payload_with_cont, note_text2)


if __name__ == '__main__':
	unittest.main()
