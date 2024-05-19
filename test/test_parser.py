import unittest
from io import StringIO
from pathlib import Path
from sys import platform
from unittest.mock import mock_open, patch

from fastgedcom.parser import (
    IS_ANSEL_INSTALLED, CharacterInsteadOfLineWarning, DuplicateXRefWarning,
    EmptyLineWarning, LevelInconsistencyWarning, LevelParsingWarning,
    LineParsingWarning, MalformedError, NothingParsedError, guess_encoding,
    parse, strict_parse
)

test_file_dir = Path(__file__).parent / "test_data"
gedcom_file_data = """0 HEAD
1 SOUR PAF
2 NAME Personal Ancestral File
2 VERS 5.2.18.0
2 CORP The Church of Jesus Christ of Latter-day Saints
3 ADDR 50 East North Temple Street
4 CONT Salt Lake City, UT 84150
4 CONT USA
1 DEST Other
1 DATE 20 May 2023
2 TIME 20:52:04
1 FILE _in_utf8.ged
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
1 LANG English
0 @I1@ INDI
1 NAME éàç /ÉÀÇ/
2 SURN ÉÀÇ
2 GIVN éàç
1 SEX U
1 _UID 8AF30D0BDE130F4E8964B9EACCAD53F6356E
1 CHAN
2 DATE 20 May 2023
3 TIME 20:51:21
0 TRLR
"""


class TestParser(unittest.TestCase):
    def test_parsing(self) -> None:
        g, w = parse(gedcom_file_data.splitlines())
        self.assertListEqual(w, [])
        self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")
        self.assertEqual(g.get_source(), gedcom_file_data)

    def test_parsing_utf8(self) -> None:
        encoding = "utf-8"
        file = test_file_dir / "in_utf8.ged"
        guess = guess_encoding(file)
        self.assertEqual(guess, encoding)
        with open(file, "r", encoding=encoding) as f:
            g, w = parse(f)
        self.assertListEqual(w, [])
        self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")
        self.assertEqual(g.get_source(), gedcom_file_data)

    def test_parsing_utf8_bom(self) -> None:
        encoding = "utf-8-sig"
        file = test_file_dir / "in_utf8_bom.ged"
        guess = guess_encoding(file)
        self.assertEqual(guess, encoding)
        with open(file, "r", encoding=encoding) as f:
            g, w = parse(f)
        self.assertListEqual(w, [])
        self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")

    def test_parsing_unicode(self) -> None:
        encoding = "utf_16"
        file = test_file_dir / "in_unicode.ged"
        guess = guess_encoding(file)
        self.assertEqual(guess, encoding)
        with open(file, "r", encoding=encoding) as f:
            g, w = parse(f)
        self.assertListEqual(w, [])
        self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")

    def test_parsing_ansi(self) -> None:
        encoding = "ansi"
        file = test_file_dir / "in_ansi.ged"
        guess = guess_encoding(file)
        self.assertEqual(guess, encoding)
        if not platform.startswith("win"):
            self.skipTest("The ansi encoding is only available on Windows")
        with open(file, "r", encoding=encoding) as f:
            g, w = parse(f)
        self.assertListEqual(w, [])
        self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")

    def test_parsing_ansel(self) -> None:
        encoding = "gedcom"
        file = test_file_dir / "in_ansel.ged"
        guess = guess_encoding(file)
        self.assertEqual(guess, encoding)
        if not IS_ANSEL_INSTALLED:
            self.skipTest("The ansel package isn't installed")
        with open(file, "r", encoding=encoding) as f:
            g, w = parse(f)
        self.assertListEqual(w, [])
        name = g["@I1@"].get_sub_line_payload("NAME")
        self.assertEqual(name, b'\xe2e\xe1a\xf0c /\xe2E\xe1A\xf0C/'.decode("gedcom"))

    def test_parsing_latin1(self) -> None:
        encoding = "iso8859-1"
        file = test_file_dir / "in_iso8859-1.ged"
        guess = guess_encoding(file)
        self.assertEqual(guess, encoding)
        with open(file, "r", encoding=encoding) as f:
            g, w = parse(f)
        self.assertListEqual(w, [])
        self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")

    def test_parsing_string_io(self) -> None:
        g, w = parse(StringIO(gedcom_file_data))
        self.assertListEqual(w, [])
        self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")
        self.assertEqual(g.get_source(), gedcom_file_data)

    def test_strict_parse(self) -> None:
        with patch('fastgedcom.parser.open') as open_mock:
            mock_open(open_mock, gedcom_file_data)
            g = strict_parse("fake file for mock")
            self.assertEqual(g["@I1@"].get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")
            self.assertEqual(g.get_source(), gedcom_file_data)

    def test_CharacterInsteadOfLineWarning(self) -> None:
        g, w = parse("0 HEAD\n0 TRLR")
        self.assertEqual(w, [CharacterInsteadOfLineWarning(1)])
        self.assertEqual(g.records, {})

    def test_EmptyLineWarning(self) -> None:
        warn_gedcom = "0 HEAD\n\n0 TRLR"
        good_gedcom = "0 HEAD\n0 TRLR"
        g, w = parse(warn_gedcom.splitlines())
        self.assertEqual(w, [EmptyLineWarning(2)])
        self.assertEqual(g, parse(good_gedcom.splitlines())[0])

    def test_LevelInconsistencyWarning_no_parent(self) -> None:
        warn_gedcom = "1 CHAR UTF-8\n0 TRLR"
        good_gedcom = "0 TRLR"
        g, w = parse(warn_gedcom.splitlines())
        self.assertEqual(w, [LevelInconsistencyWarning(1, "1 CHAR UTF-8")])
        self.assertEqual(g, parse(good_gedcom.splitlines())[0])

    def test_LevelInconsistencyWarning_wrong_parent(self) -> None:
        warn_gedcom = "0 HEAD\n2 CHAR UTF-8\n0 TRLR"
        good_gedcom = "0 HEAD\n2 CHAR UTF-8\n0 TRLR"
        g, w = parse(warn_gedcom.splitlines())
        self.assertEqual(w, [LevelInconsistencyWarning(2, "2 CHAR UTF-8")])
        self.assertEqual(g, parse(good_gedcom.splitlines())[0])

    def test_LineParsingWarning(self) -> None:
        warn_gedcom = "0 HEAD\n1 NOTE foo\nbar\n0 TRLR"
        good_gedcom = "0 HEAD\n1 NOTE foo\n0 TRLR"
        g, w = parse(warn_gedcom.splitlines())
        self.assertEqual(w, [LineParsingWarning(3, "bar")])
        self.assertEqual(g, parse(good_gedcom.splitlines())[0])

    def test_LevelParsingWarning(self) -> None:
        warn_gedcom = "0 HEAD\n1 NOTE foo\nbar baz\n0 TRLR"
        good_gedcom = "0 HEAD\n1 NOTE foo\n0 TRLR"
        g, w = parse(warn_gedcom.splitlines())
        self.assertEqual(w, [LevelParsingWarning(3, "bar baz")])
        self.assertEqual(g, parse(good_gedcom.splitlines())[0])

    def test_DuplicateXRefWarning(self) -> None:
        warn_gedcom = "0 HEAD\n0 @I1@ INDI\n0 @I1@ INDI\n0 TRLR"
        good_gedcom = "0 HEAD\n0 @I1@ INDI\n0 TRLR"
        g, w = parse(warn_gedcom.splitlines())
        self.assertEqual(w, [DuplicateXRefWarning("@I1@")])
        self.assertEqual(g, parse(good_gedcom.splitlines())[0])

    def test_NothingParsedError(self) -> None:
        with patch('fastgedcom.parser.open') as open_mock:
            mock_open(open_mock, "")
            self.assertRaises(NothingParsedError, strict_parse, "fake path for mock")

    def test_MalformedError(self) -> None:
        with patch('fastgedcom.parser.open') as open_mock:
            mock_open(open_mock, "0 HEAD\n0 @I1@ INDI\n0 @I1@ INDI\n0 TRLR")
            with self.assertRaises(MalformedError) as cm:
                strict_parse("fake path for mock")
            self.assertEqual(cm.exception.warnings, [DuplicateXRefWarning("@I1@")])


if __name__ == '__main__':
    unittest.main()
