import unittest
from datetime import datetime, UTC

from fastgedcom.helpers import (add_time, extract_int_year, extract_year,
                                format_date, remove_trailing_zeros,
                                to_datetime, to_datetime_range)


class TestDateHelpers(unittest.TestCase):
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
		self.assertEqual(format_date('ABT 2001'), '~ 2001')
		self.assertEqual(format_date('ABT 2000 BCE'), '~ -2000')
		self.assertEqual(format_date('67 BCE'), '-67')
		self.assertEqual(format_date('BEF Mar 2001 BCE'), '< Mar -2001')
		self.assertEqual(format_date('BET 2001 AND 2002'), '2001 -- 2002')
		self.assertEqual(format_date('BET 22 May 67 AND 1 Apr 67'), '22 May 67 -- 1 Apr 67')
		self.assertEqual(format_date('BET 62 BC AND 64 BC'), '-62 -- -64')
		self.assertEqual(format_date("FROM 16 Feb 1546/1547"), "16 Feb 1546/1547")

	def test_format_date_stability(self) -> None:
		dates = ('22 Mar 2001', '2001', '12 Fev 67 BCE', 'ABT 22 Mar 2001',
		         'ABT Mar 2001', 'ABT 2000 BCE', '67 BCE', 'BEF Mar 2001 BCE',
				 'BET 2001 AND 2002', 'BET 22 May 67 AND 1 Apr 67', '16 Feb 1546/1547')
		for date in dates:
			self.assertEqual(format_date(format_date(date)), format_date(date))

	def test_extract_year(self) -> None:
		self.assertEqual(extract_year(""), "")
		self.assertEqual(extract_year('22 Mar 2001'), '2001')
		self.assertEqual(extract_year('2001'), '2001')
		self.assertEqual(extract_year('2'), '2')
		self.assertEqual(extract_year('12 Fev 67 BCE'), '-67')
		self.assertEqual(extract_year('ABT 22 Mar 2001'), '~ 2001')
		self.assertEqual(extract_year('ABT 2001'), '~ 2001')
		self.assertEqual(extract_year('ABT 2000 BCE'), '~ -2000')
		self.assertEqual(extract_year('67 BCE'), '-67')
		self.assertEqual(extract_year('BEF Mar 2001 BCE'), '< -2001')
		self.assertEqual(extract_year('BET 2001 AND 2002'), '2001 -- 2002')
		self.assertEqual(extract_year('BET 22 May 67 AND 1 Apr 67'), '67')
		self.assertEqual(extract_year("FROM 16 Feb 1546/1547"), "1547")

	def test_extract_int_year(self) -> None:
		self.assertEqual(extract_int_year("", 9999), 9999)
		self.assertEqual(extract_int_year('22 Mar 2001'), 2001)
		self.assertEqual(extract_int_year('2001'), 2001)
		self.assertEqual(extract_int_year('2'), 2)
		self.assertEqual(extract_int_year('12 Fev 67 BCE'), -67)
		self.assertEqual(extract_int_year('ABT 22 Mar 2001'), 2001)
		self.assertEqual(extract_int_year('ABT 2001'), 2001)
		self.assertEqual(extract_int_year('ABT 2000 BCE'), -2000)
		self.assertEqual(extract_int_year('67 BCE'), -67)
		self.assertEqual(extract_int_year('BEF Mar 2001 BCE'), -2001)
		self.assertEqual(extract_int_year('BET 2001 AND 2002'), 2001.5)
		self.assertEqual(extract_int_year('BET 22 May 67 AND 1 Apr 67'), 67)
		self.assertEqual(extract_int_year("FROM 16 Feb 1546/1547"), 1547)

	def test_to_datetime(self) -> None:
		self.assertRaises(ValueError, to_datetime, "")
		self.assertEqual(to_datetime("", datetime.min), datetime.min)
		self.assertEqual(to_datetime('22 Mar 2001'), datetime(2001, 3, 22))
		self.assertEqual(to_datetime('2001'), datetime(2001, 1, 1))
		self.assertEqual(to_datetime('2'), datetime(2, 1, 1))
		self.assertRaises(ValueError, to_datetime, '12 Fev 67 BCE')
		self.assertEqual(to_datetime('ABT 22 Mar 2001'), datetime(2001, 3, 22))
		self.assertEqual(to_datetime('ABT 2000'), datetime(2000, 1, 1))
		self.assertRaises(ValueError, to_datetime, '67 BCE')
		self.assertRaises(ValueError, to_datetime, 'BEF Mar 2001')
		self.assertRaises(ValueError, to_datetime, 'BET 2001 AND 2002')
		self.assertRaises(ValueError, to_datetime, "FROM 16 Feb 1546/1547")

	def test_to_datetime_range(self) -> None:
		self.assertRaises(ValueError, to_datetime_range, "")
		self.assertEqual(to_datetime_range("", datetime.min), (datetime.min, datetime.min))
		self.assertRaises(ValueError, to_datetime_range, '22 Mar 2001')
		self.assertRaises(ValueError, to_datetime_range, '2001')
		self.assertRaises(ValueError, to_datetime_range, '12 Fev 67 BCE')
		self.assertRaises(ValueError, to_datetime_range, 'ABT 22 Mar 2001')
		self.assertRaises(ValueError, to_datetime_range, 'ABT 2001')
		self.assertRaises(ValueError, to_datetime, '67 BCE')
		self.assertRaises(ValueError, to_datetime, 'BEF Mar 2001')
		self.assertEqual(to_datetime_range('BET 2001 AND 2002'), (datetime(2001, 1, 1), datetime(2002, 1, 1)))
		self.assertEqual(to_datetime_range('BET 22 May 67 AND 1 Apr 67'), (datetime(67, 5, 22), datetime(67, 4, 1)))
		self.assertRaises(ValueError, to_datetime_range, 'BET 62 BC AND 64 BC')
		self.assertRaises(ValueError, to_datetime_range, "FROM 16 Feb 1546/1547")

	def test_add_time(self) -> None:
		self.assertEqual(
			add_time(datetime(1234, 12, 13), "14:15:16"),
			datetime(1234, 12, 13, 14, 15, 16)
		)
		self.assertEqual(
			add_time(datetime(1234, 12, 13), "14:15:16.123456Z"),
			datetime(1234, 12, 13, 14, 15, 16, 123456, UTC)
		)

if __name__ == '__main__':
	unittest.main()
