import unittest

from ..base import GedcomLine
from ..helpers import get_all_sub_records


class TestParser(unittest.TestCase):
	def test_sub_rec_recursive(self) -> None:
		surn = GedcomLine(2, "SURN", "BOUYER", [])
		givn = GedcomLine(2, "GIVN", "Gatien", [])
		name = GedcomLine(1, "NAME", "Gatien /BOUYER/", [surn, givn])
		sex = GedcomLine(1, "SEX", "M", [])
		indi = GedcomLine(0, "@I1@", "INDI", [name, sex])
		all_recs = list(get_all_sub_records(indi))
		self.assertListEqual(all_recs, [name, surn, givn, sex])

if __name__ == '__main__':	
	unittest.main()
