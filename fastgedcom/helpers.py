"""Utilitary functions to sort, format, or extract information."""

from typing import Iterator, overload
from datetime import datetime, time
from enum import Enum

from .base import FakeLine, TrueLine


def get_all_sub_lines(line: TrueLine) -> Iterator[TrueLine]:
	"""Recursively iterate on :py:class:`.TrueLine` of higher level.
	All lines under the given line are returned. The order is preserved
	as in the gedcom file, sub-lines come before siblings lines."""
	lines = list(line.sub_lines)
	while len(lines) > 0:
		line = lines.pop(0)
		yield line
		lines = line.sub_lines + lines

def get_source(line: TrueLine | FakeLine) -> str:
	"""Return the gedcom text equivalent for the line and its sub-lines."""
	if not line: return ""
	text = str(line) + "\n"
	for sub_line in get_all_sub_lines(line):
		text += str(sub_line) + "\n"
	return text

def format_name(name: str) -> str:
	"""Format the payload of NAME lines.
	Remove the backslash around the surname."""
	return name.replace("/", "")

def extract_name_parts(name: str) ->tuple[str, str]:
	"""Split the payload of NAME lines into the given name and the surname parts.
	The surname is the part of the payload surrounded by '/'."""
	first = name.find('/')
	second = name.find('/', first+1)
	if second == -1: return name.strip(), ""
	if (second+1 < len(name) and name[second+1] == " "
			and first > 0 and name[first-1] == " "):
		given_name = name[:first] + name[second+2:]
	else:
		given_name = name[:first] + name[second+1:]
	surname = name[first+1:second]
	return given_name.strip(), surname.strip()

class DateType(Enum):
	"""Date modifiers allowed by the Gedcom specifications.
	They can appear in payload of DATE lines."""

	BC = "{date} BC"
	"""Date before Christ. Old version from Gedcom5."""

	BCE = "{date} BCE"
	"""Date before common era. New version from Gedcom7."""

	ABT = "ABT {date}"
	"""About date."""

	EST = "EST {date}"
	"""Estimated date."""

	CAL = "CAL {date}"
	"""Calculated date."""

	BEF = "BEF {date}"
	"""Before date."""

	AFT = "AFT {date}"
	"""After date."""

	TO = "TO {date}"
	"""To date. Not prefixed by :py:attr:`FROM`."""

	FROM = "FROM {date}"
	"""From date. Not followed by :py:attr:`TO`."""

	BET_AND = "BET {date1} AND {date2}"
	"""Between date1 and date2."""

	FROM_TO = "FROM {date1} TO {date2}"
	"""From date1 to date2."""

def get_date_type(date: str) -> DateType | None:
	"""Return the modifier used by DATE line payloads.
	If no modifier is recognized, return None.
	Ignore :py:attr:`BC` and :py:attr:`BCE` and return None,
	because these modifiers can be combined with the others."""
	if date[:4]=='ABT ': return DateType.ABT
	if date[:4]=='CAL ': return DateType.CAL
	if date[:4]=='EST ': return DateType.EST
	if date[:4]=='BEF ': return DateType.BEF
	if date[:4]=='AFT ': return DateType.AFT
	if date[:4]=='BET ' and 'AND' in date: return DateType.BET_AND
	if date[:5]=='FROM ' and 'TO' in date: return DateType.FROM_TO
	if date[:5]=='FROM ': return DateType.FROM
	if date[:3]=='TO ': return DateType.TO
	return None

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

	* :py:attr:`BC` is replaced by `-`.
	* :py:attr:`BCE` is replaced by `-`.
	* :py:attr:`ABT` is replaced by `~`.
	* :py:attr:`EST` is replaced by `~`.
	* :py:attr:`CAL` is replaced by `~`.
	* :py:attr:`BEF` is replaced by `<`.
	* :py:attr:`AFT` is replaced by `>`.
	* :py:attr:`FROM` is removed.
	* :py:attr:`TO` is removed.
	* :py:attr:`BET_AND` is replaced by `--`.
	* :py:attr:`FROM_TO` is replaced by `--`.
	"""
	date = remove_trailing_zeros(date)
	if date[:4]=='BET ' and 'AND' in date:
		date = date[4:]
		date1, date2 = date.split(' AND ', 1)
		return format_date(date1) + ' -- ' + format_date(date2)
	elif date[:5]=='FROM ' and 'TO' in date:
		date = date[5:]
		date1, date2 = date.split(' TO ', 1)
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

	Keep the context of the date, i.e. replacements produced by
	:py:func:`format_date`. To extract the year but not the context,
	use :py:func:`.extract_int_year`.

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
	date_parts = formated_date.replace('/', ' ').split()
	numeric_parts = sorted(filter(lambda p: p.isdecimal() or (p[0] == '-' and p[1:].isdecimal()), date_parts), key=len)
	if len(numeric_parts) == 0:
		return ""
	year = numeric_parts[-1]
	if '~' in formated_date: year = '~ '+year
	if '<' in formated_date: year = '< '+year
	if '>' in formated_date: year = '> '+year
	return year

@overload
def extract_int_year(date: str) -> float | None: ...
@overload
def extract_int_year(date: str, default: float) -> float: ...

def extract_int_year(date: str, default: float | None = None) -> float | None:
	"""Format the payload of DATE lines.
	Return the year of the date as an integer. On failure, return the default.

	A :py:attr:`BCE` date returns a negative number. For :py:attr:`BET_AND` and
	:py:attr:`FROM_TO` date types, this function returns the median number of
	the range, hence the float type."""
	year = extract_year(date)
	if ' -- ' in year:
		str_year1, str_year2 = year.split(' -- ', 1)
		year1 = extract_int_year(str_year1)
		year2 = extract_int_year(str_year2)
		if year1 is None: return year2
		elif year2 is None: return year1
		return (year1 + year2) / 2
	year_without_context = ''.join(filter(lambda c: c.isdecimal() or c=='-', year))
	if year_without_context == "": return default
	return int(year_without_context)

def to_datetime(date: str, default: datetime | None = None) -> datetime:
	"""Convert the payload of DATE lines to datetime object.

	If default is provided, return default on failure.
	Otherwise, raise ValueError on failure.

	If no day or month is specified, the first day and month are used.

	The returned date is more precise than :py:func:`.extract_int_year`, but
	works less often. Infact, this method only works for positive dates
	(i.e. not :py:attr:`BC`) and :py:attr:`ABT`, :py:attr:`CAL`, :py:attr:`EST`
	date types. For :py:attr:`BET_AND` or :py:attr:`TO_FROM` date types, use the
	:py:func:`.to_datetime_range` function. The :py:attr:`BEF` and :py:attr:`AFT`
	date types are not supported."""
	if date[:4] in ("ABT ", "CAL ", "EST "): date = date[4:]
	year = extract_int_year(date)
	if year and 0 < year < 1000:
		four_digits_year = f"{year:04}"
		date = date.replace(str(year), four_digits_year)
	err = ValueError(f"Fail to parse {date} as a date")
	for fmt in ("%d %b %Y", "%d %b %Y", "%b %Y", "%Y"):
		try:
			return datetime.strptime(date, fmt)
		except ValueError as e:
			err = e
	if default is not None: return default
	raise err

def to_datetime_range(
		date: str,
		default: datetime | None = None,
	) -> tuple[datetime, datetime]:
	"""Convert the payload of DATE lines to datetime objects.

	If default is provided, return default on failure.
	Otherwise, raise ValueError on failure.

	A case of failure is if the date types is not :py:attr:`BET_AND`,
	or :py:attr:`FROM_TO`.

	Call :py:func:`.to_datetime` on the first and second date."""
	if date.startswith("BET ") and date.count(" AND ") == 1:
		part1, part2 = date[4:].split(" AND ")
	elif date.startswith("FROM ") and date.count(" TO ") == 1:
		part1, part2 = date[5:].split(" TO ")
	elif default is not None: return default, default
	else: raise ValueError(f"Fail to parse {date} as a date range")
	return to_datetime(part1, default), to_datetime(part2, default)

def add_time(date: datetime, time_: str) -> datetime:
	"""Parse the payload of TIME lines.
	If the time is parsed, return the datetime with its time set.
	Otherwise, return the datetime as it was.

	Note: datetime is immutable, thus the presence of a returned value."""
	try:
		t = time.fromisoformat(time_)
	except ValueError:
		return date
	return datetime.combine(date.date(), t)

def line_to_datetime(
		date: TrueLine | FakeLine,
		default: datetime | None = None,
	) -> datetime:
	"""Convert DATE lines to datetime object using the payload and the TIME sub-line."""
	dt = to_datetime(date.payload, default)
	return add_time(dt, date >= "TIME")
