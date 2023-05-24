from typing import Any, Callable, Iterator, Literal

from .base import Gedcom, GedcomLine, line_exists
from .structure import IndiRef, XRef

MINIMAL_DATE = -99999 # used to sort None dates

def get_all_sub_records(line: GedcomLine) -> Iterator[GedcomLine]:
	"""Recursively iterate on all lines under the given line."""
	sub_records = list(line.sub_rec)
	while len(sub_records) > 0:
		record = sub_records.pop(0)
		yield record
		sub_records = record.sub_rec + sub_records

def format_name(name: str | None) -> str:
	"""Format the payload of the gedcom tag NAME.
	Remove the backslash around the surname."""
	if name is None: return ""
	return name.replace("/", "")

def gender_to_ascii(gender: Literal['M', 'F'] | Any) -> Literal['♂', '♀', '⚥']:
	if gender == 'M': return '♂'
	if gender == 'F': return '♀'
	return '⚥'

def format_date(date: str | None) -> str:
	"""Format the gedcom date into a shorter string.
	Replace gedcom keywords by symbols.

	Replacements:
	- 'd BC' standing for before christ is replaced by '-d',
	- 'd BCE' or before common era with '-d',
	- 'ABT d' stading for about is replaced by '~ d',
	- 'EST d' stading for estimated is replaced by '~ d',
	- 'CAL d' stading for calculated is replaced by '~ d',
	- 'BEF d' standing for before is replaced by '< d',
	- 'AFT d' standing for after is replaced by '> d',
	- 'BET d AND d' standing for between is replaced by 'd -- d',
	- 'FROM d TO d' is replace by 'd -- d',
	- 'FROM d' is replaced by 'd',
	- 'TO d' is replaced by 'd'.
	"""
	if date is None: return ""
	date = remove_trailing_zeros(date)
	if date[:4]=='BET ' and 'AND' in date:
		date = date[4:]
		date1, date2 = date.split(' AND ', 1)
		return format_date(date1) + ' -- ' + format_date(date2)
	elif date[:5]=='FROM ' and 'TO' in date:
		date = date[5:]
		date1, date2 = date.split(' AND ', 1)
		return format_date(date1) + ' -- ' + format_date(date2)
	if date[-3:] == ' BC' or date[-4:] == ' BCE':
		date_parts = date.split(' ')
		year = date_parts[-2]
		if len(date_parts) > 2:
			date_without_year = ' '.join(date_parts[:-2])
			date = date_without_year + ' -' + year
		else: date = '-' + year
	if date[:4] in ('ABT ', 'CAL ', 'EST '): date = '~ '+date[4:]
	elif date[:4]=='BEF ': date = '< '+date[4:]
	elif date[:4]=='AFT ': date = '> '+date[4:]
	elif date[:5]=='FROM ': date = date[5:]
	elif date[:3]=='TO ': date = date[3:]
	return date

def remove_trailing_zeros(date: str) -> str:
	k = 0
	while k+1 < len(date):
		if date[k]=='0' and (k==0 or (k>0 and (date[k-1].isspace() or date[k-1] == '-'))):
			date = date[:k] + date[k+1:]
		else:
			k += 1
	return date

def extract_year(date: str | None) -> str:
	"""Return the only year of the date.
	The parameter is the gedcom date or the formatted date string.
	Keep the context of the date: '-', '~', '<', '>' and '--'."""
	formated_date = format_date(date)
	if ' -- ' in formated_date:
		first_date, second_date = formated_date.split(' -- ', 1)
		first_year = extract_year(first_date)
		second_year = extract_year(second_date)
		if first_year == second_year: return first_year
		return first_year + ' -- ' + second_year
	date_parts = formated_date.split()
	numeric_parts = sorted(filter(lambda p: p.isdecimal() or (p[0] == '-' and p[1:].isdecimal()), date_parts), key=len)
	if len(numeric_parts) == 0:
		return ""
	year = numeric_parts[-1]
	if '~' in formated_date: year = '~ '+year
	if '<' in formated_date: year = '< '+year
	if '>' in formated_date: year = '> '+year
	return year

def extract_int_year(date: str | None) -> float | None:
	"""Return the year of the date as an integer.
	Keep the context: A date BCE returns a negative number.
	A date range of type `between` or `from-to` returns the median number of the range."""
	year = extract_year(date)
	if ' -- ' in year:
		str_year1, str_year2 = year.split(' -- ', 1)
		year1 = extract_int_year(str_year1)
		year2 = extract_int_year(str_year2)
		if year1 is None: return year2
		elif year2 is None: return year1
		return (year1 + year2) / 2
	year_without_context = ''.join(filter(lambda c: c.isdecimal() or c=='-', year))
	if year_without_context == "": return None
	return int(year_without_context)


def sorting_key_indi_birth(gedcom: Gedcom) -> Callable[[IndiRef], float]:
	def get_sorting_key_indi_birth(indi: IndiRef) -> float:
		birth_year = extract_int_year((gedcom[indi] > "BIRT") >= "DATE")
		return -MINIMAL_DATE if birth_year is None else birth_year
	return get_sorting_key_indi_birth

def sorting_key_indi_union(
	gedcom: Gedcom, ref_indi: IndiRef
) -> Callable[[IndiRef], float]:
	def get_sorting_key_indi_union(indi: IndiRef) -> float:
		unions = gedcom.get_unions(ref_indi, indi)
		if len(unions) == 0: return -MINIMAL_DATE
		union_year = extract_int_year(gedcom[unions[0]] >= "DATE")
		return -MINIMAL_DATE if union_year is None else union_year
	return get_sorting_key_indi_union


def get_gedcom_data(gedcom: Gedcom, xref: XRef) -> str:
	"""Return all the contents of the gedcom under this level 0 id (person id, family id, source id, ...)."""
	rec = gedcom.get_record(xref)
	if not line_exists(rec): return ""
	text = str(rec) + "\n"
	for sub_rec in get_all_sub_records(rec):
		text += str(sub_rec) + "\n"
	return text
