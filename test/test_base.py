import unittest

from fastgedcom.base import Document, TrueLine, fake_line


class TestTrueLine(unittest.TestCase):
    def test_get_sub_line(self) -> None:
        name = TrueLine(1, "NAME", "éàç /ÉÀÇ/")
        sex = TrueLine(1, "SEX", "U")
        indi = TrueLine(0, "@I1@", "INDI", [name, sex])
        self.assertEqual(indi.get_sub_line("SEX"), sex)
        self.assertEqual(indi > "SEX", sex)
        self.assertEqual(indi > "BIRT", fake_line)

    def test_get_sub_lines(self) -> None:
        name = TrueLine(1, "NAME", "éàç /ÉÀÇ/")
        fam1 = TrueLine(1, "FAMS", "@F1@")
        fam2 = TrueLine(1, "FAMS", "@F2@")
        indi = TrueLine(0, "@I1@", "INDI", [fam1, name, fam2])
        self.assertEqual(indi.get_sub_lines("FAMS"), [fam1, fam2])
        self.assertEqual(indi >> "FAMS", [fam1, fam2])
        self.assertEqual(indi >> "FAMC", [])

    def test_iter_on_sublines(self) -> None:
        name = TrueLine(1, "NAME", "éàç /ÉÀÇ/")
        fam1 = TrueLine(1, "FAMS", "@F1@")
        fam2 = TrueLine(1, "FAMS", "@F2@")
        indi = TrueLine(0, "@I1@", "INDI", [fam1, name, fam2])
        self.assertEqual(list(indi), [fam1, name, fam2])
        self.assertEqual(list(TrueLine(0, "@I2@", "INDI")), [])

    def test_get_sub_line_payload(self) -> None:
        name = TrueLine(1, "NAME", "éàç /ÉÀÇ/")
        indi = TrueLine(0, "@I1@", "INDI", [name])
        self.assertEqual(indi.get_sub_line_payload("NAME"), "éàç /ÉÀÇ/")
        self.assertEqual(indi >= "NAME", "éàç /ÉÀÇ/")
        self.assertEqual(indi >= "SEX", "")

    def test_get_all_sub_lines(self) -> None:
        surn = TrueLine(2, "SURN", "ÉÀÇ")
        givn = TrueLine(2, "GIVN", "éàç")
        name = TrueLine(1, "NAME", "éàç /ÉÀÇ/", [surn, givn])
        sex = TrueLine(1, "SEX", "U")
        indi = TrueLine(0, "@I1@", "INDI", [name, sex])
        self.assertEqual(list(indi.get_all_sub_lines()), [name, surn, givn, sex])

    def test_get_source(self) -> None:
        surn = TrueLine(2, "SURN", "ÉÀÇ")
        givn = TrueLine(2, "GIVN", "éàç")
        name = TrueLine(1, "NAME", "éàç /ÉÀÇ/", [surn, givn])
        sex = TrueLine(1, "SEX", "U")
        indi = TrueLine(0, "@I1@", "INDI", [name, sex])
        self.assertEqual(
            indi.get_source(),
            "0 @I1@ INDI\n1 NAME éàç /ÉÀÇ/\n2 SURN ÉÀÇ\n2 GIVN éàç\n1 SEX U\n",
        )

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


class TestFakeLine(unittest.TestCase):
    def test_get_sub_line(self) -> None:
        self.assertEqual(fake_line.get_sub_line("SEX"), fake_line)
        self.assertEqual(fake_line > "SEX", fake_line)

    def test_get_sub_lines(self) -> None:
        self.assertEqual(fake_line.get_sub_lines("FAMS"), [])
        self.assertEqual(fake_line >> "FAMS", [])

    def test_iter_on_sublines(self) -> None:
        self.assertEqual(list(fake_line), [])

    def test_get_sub_line_payload(self) -> None:
        self.assertEqual(fake_line.get_sub_line_payload("NAME"), "")
        self.assertEqual(fake_line >= "NAME", "")

    def test_get_all_sub_lines(self) -> None:
        self.assertEqual(list(fake_line.get_all_sub_lines()), [])

    def test_get_source(self) -> None:
        self.assertEqual(fake_line.get_source(), "")

    def test_payload_with_cont(self) -> None:
        self.assertEqual(fake_line.payload_with_cont, "")


class TestDocument(unittest.TestCase):
    def test_contains(self) -> None:
        doc = Document()
        doc.records["@I1@"] = TrueLine(0, "@I1@", "INDI")
        self.assertEqual("@I1@" in doc, True)
        self.assertEqual("@I9@" in doc, False)

    def test_get_record(self) -> None:
        doc = Document()
        indi = doc.records["@I1@"] = TrueLine(0, "@I1@", "INDI")
        self.assertEqual(doc.get_record("@I1@"), indi)
        self.assertEqual(doc["@I1@"], indi)
        self.assertEqual(doc["@I9@"], fake_line)

    def test_get_records(self) -> None:
        doc = Document()
        indi1 = doc.records["@I1@"] = TrueLine(0, "@I1@", "INDI")
        indi2 = doc.records["@I2@"] = TrueLine(0, "@I2@", "INDI")
        doc.records["@F1@"] = TrueLine(0, "@F1@", "FAM")
        self.assertEqual(list(doc.get_records("INDI")), [indi1, indi2])
        self.assertEqual(list(doc >> "INDI"), [indi1, indi2])

    def test_iterable(self) -> None:
        doc = Document()
        indi1 = doc.records["@I1@"] = TrueLine(0, "@I1@", "INDI")
        indi2 = doc.records["@I2@"] = TrueLine(0, "@I2@", "INDI")
        fam = doc.records["@F1@"] = TrueLine(0, "@F1@", "FAM")
        self.assertEqual(list(doc), [indi1, indi2, fam])

    def test_get_all_lines(self) -> None:
        doc = Document()
        indi1 = doc.records["@I1@"] = TrueLine(0, "@I1@", "INDI")
        surn = TrueLine(2, "SURN", "ÉÀÇ")
        givn = TrueLine(2, "GIVN", "éàç")
        name = TrueLine(1, "NAME", "éàç /ÉÀÇ/", [surn, givn])
        sex = TrueLine(1, "SEX", "U")
        indi = TrueLine(0, "@I2@", "INDI", [name, sex])
        indi2 = doc.records["@I2@"] = indi
        fam = doc.records["@F1@"] = TrueLine(0, "@F1@", "FAM")
        self.assertEqual(list(doc.get_all_lines()), [
            [indi1],
            [indi2],
            [indi2, name],
            [indi2, name, surn],
            [indi2, name, givn],
            [indi2, sex],
            [fam],
        ])

    def test_get_source(self) -> None:
        doc = Document()
        doc.records["@I1@"] = TrueLine(0, "@I1@", "INDI")
        doc.records["@I2@"] = TrueLine(0, "@I2@", "INDI", [TrueLine(1, "NAME", "éàç /ÉÀÇ/")])
        doc.records["@F1@"] = TrueLine(0, "@F1@", "FAM")
        self.assertEqual(doc.get_source(), "0 @I1@ INDI\n0 @I2@ INDI\n1 NAME éàç /ÉÀÇ/\n0 @F1@ FAM\n")


if __name__ == '__main__':
    unittest.main()
