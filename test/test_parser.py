import unittest
from typing import Iterable
from io import StringIO
from pathlib import Path

from fastgedcom.base import TrueLine
from fastgedcom.helpers import get_all_sub_lines
from fastgedcom.parser import (CharacterInsteadOfLineWarning,
                               DuplicateXRefWarning, EmptyLineWarning,
                               LevelInconsistencyWarning, LevelParsingWarning,
                               LineParsingWarning, guess_encoding, parse)

file_utf8 = Path(__file__).parent / "test_data" / "in_utf8.ged"
file_utf8_bom = Path(__file__).parent / "test_data" / "in_utf8_bom.ged"
file_ansi =  Path(__file__).parent / "test_data" / "in_ansi.ged"
file_ansel =  Path(__file__).parent / "test_data" / "in_ansel.ged"
file_unicode =  Path(__file__).parent / "test_data" / "in_unicode.ged"
file_iso8859_1 = Path(__file__).parent / "test_data" / "in_iso8859-1.ged"

class TestParser(unittest.TestCase):
	def _test_parsing(self, lines_to_parse: Iterable[str], expected_number_of_lines: int) -> None:
		g, w = parse(lines_to_parse)
		self.assertListEqual(w, [])
		indi = g.get_record("@I1@")
		self.assertIsNotNone(indi) ; assert(indi)
		name = indi.get_sub_line_payload("NAME")
		self.assertEqual(name, "éàç /ÉÀÇ/")
		nb_lines = len(g.records) + sum(1
			for r in g for _ in get_all_sub_lines(r))
		self.assertEqual(nb_lines, expected_number_of_lines)

	def test_parsing_utf8(self) -> None:
		with open(file_utf8, "r", encoding="utf-8") as f:
			self._test_parsing(f, 27)

	def test_parsing_utf8_bom(self) -> None:
		with open(file_utf8_bom, "r", encoding="utf-8-sig") as f:
			self._test_parsing(f, 27)

	def test_parsing_unicode(self) -> None:
		with open(file_unicode, "r", encoding="utf-16") as f:
			self._test_parsing(f, 27)

	def test_parsing_ansi(self) -> None:
		with open(file_ansi, "r", encoding="ansi") as f:
			self._test_parsing(f, 27)

	def test_parsing_ansel(self) -> None:
		with open(file_ansel, "r", encoding="gedcom") as f:
			g, w = parse(f)
			self.assertListEqual(w, [])
			indi = g.get_record("@I1@")
			self.assertIsNotNone(indi) ; assert(indi)
			name = indi.get_sub_line_payload("NAME")
			ansel_name = b'\xe2e\xe1a\xf0c /\xe2E\xe1A\xf0C/'.decode("gedcom")
			self.assertEqual(name, ansel_name)
			nb_lines = len(g.records) + sum(1
				for r in g for _ in get_all_sub_lines(r))
			self.assertEqual(nb_lines, 27)

	def test_guess_parsing(self) -> None:
		pairs = {
			file_utf8: "utf-8-sig",
			file_utf8_bom: "utf-8-sig",
			file_unicode: "utf-16",
			file_ansi: "ansi",
			file_ansel: "gedcom",
			file_iso8859_1: "iso8859-1",
		}
		for filename, encoding in pairs.items():
			guess = guess_encoding(filename)
			guess_lower = guess.lower() if guess else None
			self.assertEqual(guess_lower, encoding, f"File: {filename}")

	def test_string_io_parsing(self) -> None:
		stream = StringIO("0 HEAD\n1 GEDC\n2 VERS 5.5\n1 CHAR UTF-8\n0 @I1@ INDI\n1 NAME éàç /ÉÀÇ/\n2 SURN ÉÀÇ\n2 GIVN éàç\n1 SEX M")
		self._test_parsing(stream, 9)
	
	def test_test_parsing(self) -> None:
		text = """
		0 HEAD
		1 GEDC
		2 VERS 5.5
		1 CHAR UTF-8
		0 @I1@ INDI
		1 NAME éàç /ÉÀÇ/
		2 SURN ÉÀÇ
		2 GIVN éàç
		1 SEX M
		"""
		self._test_parsing(text.strip().splitlines(), 9)

	def test_warnings(self) -> None:
		d, ws = parse("O HEAD\n0 TRLR")
		self.assertTrue(d == parse(StringIO(""))[0])
		self.assertTrue(any(isinstance(w, CharacterInsteadOfLineWarning) for w in ws))
		d, ws = parse(StringIO("0 HEAD\n0 @I1@ INDI\n\n0 TRLR"))
		self.assertTrue(d == parse(StringIO("0 HEAD\n0 @I1@ INDI\n0 TRLR"))[0])
		self.assertTrue(any(isinstance(w, EmptyLineWarning) for w in ws))
		d, ws = parse(StringIO("1 CHAR UTF-8\n0 TRLR"))
		self.assertTrue(d.records == {"TRLR":TrueLine(0, "TRLR", "")})
		self.assertTrue(any(isinstance(w, LevelInconsistencyWarning) for w in ws))
		d, ws = parse(StringIO("0 HEAD\n1 NOTE foo\nbar\n0 TRLR"))
		self.assertTrue(d == parse(StringIO("0 HEAD\n1 NOTE foo\n0 TRLR"))[0])
		self.assertTrue(any(isinstance(w, LineParsingWarning) for w in ws))
		d, ws = parse(StringIO("0 HEAD\n1 NOTE foo\nbar baz\n0 TRLR"))
		self.assertTrue(d == parse(StringIO("0 HEAD\n1 NOTE foo\n0 TRLR"))[0])
		self.assertTrue(any(isinstance(w, LevelParsingWarning) for w in ws))
		d, ws = parse(StringIO("0 HEAD\n0 @I1@ INDI\n0 @I1@ INDI\n0 TRLR"))
		self.assertTrue(d == parse(StringIO("0 HEAD\n0 @I1@ INDI\n0 TRLR"))[0])
		self.assertTrue(any(isinstance(w, DuplicateXRefWarning) for w in ws))


if __name__ == '__main__':
	unittest.main()
