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
			TrueLine(2, "CONT", "on several"),
			TrueLine(2, "CONT", "lines"),
		])
		self.assertEqual(note_line1.payload_with_cont, note_text1)
		note_text2 = "This is a very long text that is split"
		note_line2 = TrueLine(1, "NOTE", "This is a very", [
			TrueLine(2, "CONC", " long text th"),
			TrueLine(2, "CONC", "at is split"),
		])
		self.assertEqual(note_line2.payload_with_cont, note_text2)
		note_text3 = "This text is on several lines:\nTo present a very long text that is split.\n\nAnd a second one:\nAlso a very long sentence that is split."
		note_line3 = TrueLine(1, "NOTE", "This text is on several lines:", [
			TrueLine(2, "CONT", "To present a very long"),
			TrueLine(2, "CONC", " text that is split."),
			TrueLine(2, "CONT", ""),
			TrueLine(2, "CONT", "And a second one:"),
			TrueLine(2, "CONT", "Also a very long sent"),
			TrueLine(2, "CONC", "ence that is split."),
		])
		self.assertEqual(note_line3.payload_with_cont, note_text3)


if __name__ == '__main__':
	unittest.main()
