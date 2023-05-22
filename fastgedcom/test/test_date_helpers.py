import unittest

from ..gedcom_helper import (format_date, remove_trailing_zeros,
                             extract_int_year, extract_year)


class TestParser(unittest.TestCase):
	def test_remove_trailing_zeros(self) -> None:
		self.assertEqual(remove_trailing_zeros(""), "")
		self.assertEqual(remove_trailing_zeros("0"), "0")
		self.assertEqual(remove_trailing_zeros("00"), "0")
		self.assertEqual(remove_trailing_zeros("10"), "10")
		self.assertEqual(remove_trailing_zeros("010"), "10")
		self.assertEqual(remove_trailing_zeros("001"), "1")
		self.assertEqual(remove_trailing_zeros("00"), "0")
		self.assertEqual(remove_trailing_zeros("10 May 067"), "10 May 67")
		self.assertEqual(remove_trailing_zeros("-10"), "-10")
		self.assertEqual(remove_trailing_zeros("-010"), "-10")
	
	def test_format_date(self) -> None:
		self.assertEqual(format_date(""), "")
		self.assertEqual(format_date('22 Mar 2001'), '22 Mar 2001')
		self.assertEqual(format_date('2001'), '2001')
		self.assertEqual(format_date('12 Fev 67 BCE'), '12 Fev -67')
		self.assertEqual(format_date('ABT 22 Mar 2001'), '~ 22 Mar 2001')
		self.assertEqual(format_date('ABT Mar 2001'), '~ Mar 2001')
		self.assertEqual(format_date('ABT 2000 BCE'), '~ -2000')
		self.assertEqual(format_date('67 BCE'), '-67')
		self.assertEqual(format_date('BEF Mar 2001 BCE'), '< Mar -2001')
		self.assertEqual(format_date('BET 2001 AND 2002'), '2001 -- 2002')
		self.assertEqual(format_date('BET 22 May 67 AND 1 Apr 67'), '22 May 67 -- 1 Apr 67')
		self.assertEqual(format_date('BET 62 BC AND 64 BC'), '-62 -- -64')
	
	def test_format_date_stability(self) -> None:
		dates = ('22 Mar 2001', '2001', '12 Fev 67 BCE', 'ABT 22 Mar 2001',
		         'ABT Mar 2001', 'ABT 2000 BCE', '67 BCE', 'BEF Mar 2001 BCE',
				 'BET 2001 AND 2002', 'BET 22 May 67 AND 1 Apr 67')
		for date in dates:
			self.assertEqual(format_date(format_date(date)), format_date(date))

	def test_extract_year(self) -> None:
		self.assertEqual(extract_year(""), "")
		self.assertEqual(extract_year('22 Mar 2001'), '2001')
		self.assertEqual(extract_year('2001'), '2001')
		self.assertEqual(extract_year('12 Fev 67 BCE'), '-67')
		self.assertEqual(extract_year('ABT 22 Mar 2001'), '~ 2001')
		self.assertEqual(extract_year('ABT Mar 2001'), '~ 2001')
		self.assertEqual(extract_year('ABT 2000 BCE'), '~ -2000')
		self.assertEqual(extract_year('67 BCE'), '-67')
		self.assertEqual(extract_year('BEF Mar 2001 BCE'), '< -2001')
		self.assertEqual(extract_year('BET 2001 AND 2002'), '2001 -- 2002')
		self.assertEqual(extract_year('BET 22 May 67 AND 1 Apr 67'), '67')
	
	def test_extract_int_year(self) -> None:
		self.assertEqual(extract_int_year(""), None)
		self.assertEqual(extract_int_year('22 Mar 2001'), 2001)
		self.assertEqual(extract_int_year('2001'), 2001)
		self.assertEqual(extract_int_year('12 Fev 67 BCE'), -67)
		self.assertEqual(extract_int_year('ABT 22 Mar 2001'), 2001)
		self.assertEqual(extract_int_year('ABT Mar 2001'), 2001)
		self.assertEqual(extract_int_year('ABT 2000 BCE'), -2000)
		self.assertEqual(extract_int_year('67 BCE'), -67)
		self.assertEqual(extract_int_year('BEF Mar 2001 BCE'), -2001)
		self.assertEqual(extract_int_year('BET 2001 AND 2002'), 2001.5)
		self.assertEqual(extract_int_year('BET 22 May 67 AND 1 Apr 67'), 67)


if __name__ == '__main__':
	unittest.main()
