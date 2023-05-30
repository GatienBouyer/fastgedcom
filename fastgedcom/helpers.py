"""Utilitary functions to sort, format, or extract information."""

from typing import Callable, Iterator, Literal

from .base import Document, FakeLine, IndiRef, TrueLine, is_true
from .family_aid import FamilyAid

MINIMAL_DATE = -99999
"""Default year when sorting dates.
Used when the dates cannot be convert to an integer using
:py:func:`.extract_int_year`."""

def get_all_sub_lines(line: TrueLine) -> Iterator[TrueLine]:
	"""Recursively iterate on :py:class:`.TrueLine` of higher level.
	All lines under the given line are returned. The order is preserved
	as in the gedcom file, sub-lines come before siblings lines."""
	lines = list(line.sub_lines)
	while len(lines) > 0:
		line = lines.pop(0)
		yield line
		lines = line.sub_lines + lines

def get_source_infos(line: TrueLine | FakeLine) -> str:
	"""Return the gedcom text equivalent for the line and its sub-lines."""
	if not is_true(line): return ""
	text = str(line) + "\n"
	for sub_line in get_all_sub_lines(line):
		text += str(sub_line) + "\n"
	return text

def format_name(name: str) -> str:
	"""Format the payload of NAME lines.
	Remove the backslash around the surname."""
	return name.replace("/", "")

def gender_to_ascii(gender: Literal['M', 'F'] | str) -> Literal['♂', '♀', '⚥']:
	"""Format the payload of SEX lines."""
	if gender == 'M': return '♂'
	if gender == 'F': return '♀'
	return '⚥'

def remove_trailing_zeros(date: str) -> str:
	"""Removes useless 0 prefixing numbers."""
	k = 0
	while k+1 < len(date):
		if date[k]!='0': k += 1
		elif k==0 or date[k-1].isspace() or date[k-1] == '-':
			date = date[:k] + date[k+1:]
		else: k += 1
	return date

def format_date(date: str) -> str:
	"""Format the payload of DATE lines.
	Return a short string representation of the date by
	replacing gedcom keywords by symbols.

	Replacements:

	* 'd BC' standing for before christ is replaced by '-d',
	* 'd BCE' or before common era with '-d',
	* 'ABT d' stading for about is replaced by '~ d',
	* 'EST d' stading for estimated is replaced by '~ d',
	* 'CAL d' stading for calculated is replaced by '~ d',
	* 'BEF d' standing for before is replaced by '< d',
	* 'AFT d' standing for after is replaced by '> d',
	* 'BET d AND d' standing for between is replaced by 'd -- d',
	* 'FROM d TO d' is replace by 'd -- d',
	* 'FROM d' is replaced by 'd',
	* 'TO d' is replaced by 'd'.
	"""
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

def extract_year(date: str) -> str:
	"""Format the payload of DATE lines.

	Keep the context of the date: '-', '~', '<', '>' and '--'.
	To extract year but not the context, use :py:func:`.extract_int_year`.

	Remove the day and the month if present.
	The parameter is the DATE payload or the formatted date string.
	"""
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

def extract_int_year(date: str) -> float | None:
	"""Format the payload of DATE lines.
	Return the year of the date as an integer.

	Keep the context: A date BCE returns a negative number.
	For a date range of type `between` or `from-to`, this function
	returns the median number of the range, hence the float type.
	Return None on failure."""
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


def sorting_key_indi_birth(document: Document) -> Callable[[IndiRef | None], float]:
	"""Function that can be used to sort individuals by year of birth.

	Usage:
	:code:`sorted(individuals, key=sorting_key_indi_birth(document)`
	"""
	def get_sorting_key_indi_birth(indi: IndiRef | None) -> float:
		if indi is None: return MINIMAL_DATE
		birth_year = extract_int_year((document[indi] > "BIRT") >= "DATE")
		return MINIMAL_DATE if birth_year is None else birth_year
	return get_sorting_key_indi_birth

def sorting_key_indi_union_with(
	document: Document, ref_indi: IndiRef
) -> Callable[[IndiRef | None], float]:
	"""Function that can be used to sort the spouses of someone by date of union.

	The optionnal :py:class:`.FamilyAid` object can be passed to avoid
	repetitive creation of that object.

	Usage:
	:code:`sorted(spouses_of_indiX, key=sorting_key_indi_union_with(document, indiX)`
	"""
	family_aid = FamilyAid(document)
	def get_sorting_key_indi_union_with(indi: IndiRef | None) -> float:
		if indi is None: return MINIMAL_DATE
		unions = family_aid.get_unions_with(ref_indi, indi)
		if len(unions) == 0: return MINIMAL_DATE
		union_year = extract_int_year(document[unions[0]] >= "DATE")
		return MINIMAL_DATE if union_year is None else union_year
	return get_sorting_key_indi_union_with
