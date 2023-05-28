import unittest

from fastgedcom.base import TrueLine
from fastgedcom.helpers import get_all_sub_lines


class TestParser(unittest.TestCase):
	def test_sub_rec_recursive(self) -> None:
		surn = TrueLine(2, "SURN", "BOUYER", [])
		givn = TrueLine(2, "GIVN", "Gatien", [])
		name = TrueLine(1, "NAME", "Gatien /BOUYER/", [surn, givn])
		sex = TrueLine(1, "SEX", "M", [])
		indi = TrueLine(0, "@I1@", "INDI", [name, sex])
		all_recs = list(get_all_sub_lines(indi))
		self.assertListEqual(all_recs, [name, surn, givn, sex])

if __name__ == '__main__':	
	unittest.main()
