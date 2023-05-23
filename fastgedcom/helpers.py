from typing import Callable, Literal, NamedTuple, cast
from pathlib import Path

from .base import Gedcom
from .structure import FamRef, IndiRef, XRef

GENDER = Literal['M', 'F', 'U']

MINIMAL_DATE = -99999 # used to sort None dates

def format_name(name: str) -> str:
	"""Format the payload of the gedcom tag NAME.
	Remove the backslash around the surname."""
	return name.replace("/", "")

def gender_to_ascii(gender: GENDER) -> str:
	if gender == 'M': return '♂'
	if gender == 'F': return '♀'
	return '°'

def format_date(date: str) -> str:
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

def extract_year(date: str) -> str:
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

def extract_int_year(date: str) -> float | None:
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
		birth_year = extract_int_year(get_birth_date(gedcom, indi))
		return -MINIMAL_DATE if birth_year is None else birth_year
	return get_sorting_key_indi_birth

def sorting_key_indi_union(gedcom: Gedcom, ref_indi: IndiRef) -> Callable[[IndiRef], float]:
	def get_sorting_key_indi_union(indi: IndiRef) -> float:
		unions = gedcom.get_unions(ref_indi, indi)
		if len(unions) == 0: return -MINIMAL_DATE
		union_year = extract_int_year(get_union_date(gedcom, unions[0]))
		return -MINIMAL_DATE if union_year is None else union_year
	return get_sorting_key_indi_union


def is_record_existing(gedcom: Gedcom, xref: XRef) -> bool:
	return gedcom.get_record(xref) is not None

def get_father(gedcom: Gedcom, xref: IndiRef) -> IndiRef | None:
	"""Return the id of the father of the person.
	Parameter is the id of the person.
	Return the father id or None in case of missing data."""
	return gedcom.get_parents(xref)[0]

def get_mother(gedcom: Gedcom, xref: IndiRef) -> IndiRef | None:
	"""Return the id of the mother of the person.
	Parameter is the id of the person.
	Return the mother id or None in case of missing data."""
	return gedcom.get_parents(xref)[1]

def get_gender(gedcom: Gedcom, xref: IndiRef) -> GENDER:
	"""Return the gender of the person.
	Note: There is only 3 genders in gedcom specifications: M, F and U."""
	indi = gedcom.get_record(xref)
	if indi is None: return 'U'
	sex = cast(GENDER, indi.get_sub_record_payload("SEX"))
	return "U" if sex is None else sex

def get_name(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return a formatted version of the full name of the person."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	name = indi.get_sub_record_payload("NAME")
	return "" if name is None else format_name(name)

def get_lastname(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the family name of the person. E.g. : de Bourdon"""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	name = indi.get_sub_record("NAME")
	if name is None: return ""
	surn = name.get_sub_record_payload("SURN")
	return "" if surn is None else surn

def get_firstname(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the given names of the person. E.g. : Ana Maria Mauricia"""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	name = indi.get_sub_record("NAME")
	if name is None: return ""
	given = name.get_sub_record_payload("GIVN")
	return "" if given is None else given

def get_name_given(gedcom: Gedcom, xref: IndiRef) -> tuple[str, str]:
	"""Return the last name and the given name(s)."""
	indi = gedcom.get_record(xref)
	if indi is None: return "", ""
	name = indi.get_sub_record("NAME")
	if name is None: return "", ""
	surn = name.get_sub_record_payload("SURN")
	given = name.get_sub_record_payload("GIVN")
	return "" if surn is None else surn, "" if given is None else given

def get_alias(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the alias of the person look for '_AKA' record."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	name = indi.get_sub_record("NAME")
	if name is None: return ""
	alias = name.get_sub_record_payload("_AKA")
	return "" if alias is None else alias

def get_birth(gedcom: Gedcom, xref: IndiRef) -> tuple[str, str]:
	"""Return the date and the place of the birth of the person.
	note: date is formatted in a string with format_date"""
	indi = gedcom.get_record(xref)
	if indi is None: return "", ""
	birth = indi.get_sub_record("BIRT")
	if birth is None: return "", ""
	place = birth.get_sub_record_payload("PLAC")
	date = birth.get_sub_record_payload("DATE")
	return ("" if date is None else format_date(date)), ("" if place is None else place)

def get_birth_place(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the place of the birth of the person."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	birth = indi.get_sub_record("BIRT")
	if birth is None: return ""
	place = birth.get_sub_record_payload("PLAC")
	return "" if place is None else place

def get_birth_date(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the date of the birth of the person."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	birth = indi.get_sub_record("BIRT")
	if birth is None: return ""
	date = birth.get_sub_record_payload("DATE")
	return "" if date is None else format_date(date)

def get_death(gedcom: Gedcom, xref: IndiRef) -> tuple[str, str]:
	"""Return the date and the place of the death of the person
	note: date is formatted in a string with format_date"""
	indi = gedcom.get_record(xref)
	if indi is None: return "", ""
	death = indi.get_sub_record("DEAT")
	if death is None: return "", ""
	place = death.get_sub_record_payload("PLAC")
	date = death.get_sub_record_payload("DATE")
	return ("" if date is None else format_date(date)), ("" if place is None else place)

def get_death_place(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the place of the death of the person."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	death = indi.get_sub_record("DEAT")
	if death is None: return ""
	place = death.get_sub_record_payload("PLAC")
	return "" if place is None else place

def get_death_date(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the date of the death of the person."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	death = indi.get_sub_record("DEAT")
	if death is None: return ""
	date = death.get_sub_record_payload("DATE")
	return "" if date is None else format_date(date)

def get_sorted_spouses(gedcom: Gedcom, xref: IndiRef) -> list[IndiRef]:
	"""Return the list of spouse id of the person"""
	return sorted(gedcom.get_spouses(xref), key=sorting_key_indi_union(gedcom, xref))

def get_sorted_children(gedcom: Gedcom, xref: IndiRef) -> list[IndiRef]:
	"""Return the list of child ids that the person had (regardless of the spouse)."""
	return sorted(gedcom.get_children(xref), key=sorting_key_indi_birth(gedcom))

def get_sorted_spouse_and_children(gedcom: Gedcom, xref: IndiRef) -> list[tuple[IndiRef | None, list[IndiRef]]]:
	"""Return the list of tuple (spouse id, child id list) of the person
	The spouse id is None if the data is missing.
	Without children, the list is empty"""
	unions_raw = gedcom.get_spouse_children_per_union(xref)
	unions = ((spouse, sorted(children, key=sorting_key_indi_birth(gedcom))) for spouse, children in unions_raw)
	return sorted(unions, key=lambda s_ch:sorting_key_indi_union(gedcom, xref)(s_ch[0]) if s_ch[0] else MINIMAL_DATE)

def get_sorted_children_with(gedcom: Gedcom, xref: IndiRef, spouse_xref: IndiRef) -> list[IndiRef]:
	"""Return the list of child ids that the person had with the spouse."""
	return sorted(gedcom.get_children(xref, spouse_xref), key=sorting_key_indi_birth(gedcom))

def get_note(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the content of the NOTE tag of the person. None if nothing."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	note = indi.get_sub_record('NOTE')
	if note is None: return ""
	text = note.payload
	if text is None: text = ""
	for cont in note.get_sub_records('CONT'):
		text += '\n'
		text_part = cont.payload
		if text_part is not None: text += text_part
	return text

def get_job(gedcom: Gedcom, xref: IndiRef) -> str:
	"""Return the occupation (tag 'OCCU' in the gedcom) of the person.
	None if the data is missing."""
	indi = gedcom.get_record(xref)
	if indi is None: return ""
	occupation = indi.get_sub_record_payload('OCCU')
	return occupation if occupation is not None else ""

def get_union_date(gedcom: Gedcom, xref: FamRef) -> str:
	"""Return the date of the union.
	Parameters are the family id."""
	fam = gedcom.get_record(xref)
	if fam is None: return ""
	marriage = fam.get_sub_record("MARR")
	if marriage is None: return ""
	date = marriage.get_sub_record_payload("DATE")
	return "" if date is None else format_date(date)

def get_union_place(gedcom: Gedcom, xref: FamRef) -> str:
	"""Return the place of the union.
	Parameters are the family id."""
	fam = gedcom.get_record(xref)
	if fam is None: return ""
	marriage = fam.get_sub_record("MARR")
	if marriage is None: return ""
	place = marriage.get_sub_record_payload("PLAC")
	return "" if place is None else place

def get_union_date_place(gedcom: Gedcom, xref: FamRef) -> tuple[str, str]:
	"""Return the date and place of the union.
	Parameters are the family id (1 FAM_ID) or the couple ids (2 INDI_ID)."""
	fam = gedcom.get_record(xref)
	if fam is None: return "", ""
	marriage = fam.get_sub_record("MARR")
	if marriage is None: return "", ""
	date = marriage.get_sub_record_payload("DATE")
	place = marriage.get_sub_record_payload("PLAC")
	return "" if date is None else format_date(date), "" if place is None else place

def get_sorted_siblings(gedcom: Gedcom, xref: IndiRef) -> list[IndiRef]:
	"""Return the list of ids of the siblings of the person."""
	return sorted(gedcom.get_siblings(xref), key=sorting_key_indi_birth(gedcom))

def get_sorted_stepsiblings(gedcom: Gedcom, xref: IndiRef) -> list[IndiRef]:
	"""Return the list of ids of the step_siblings of the person."""
	return sorted(gedcom.get_stepsiblings(xref), key=sorting_key_indi_birth(gedcom))

def get_gedcom_data(gedcom: Gedcom, xref: XRef) -> str:
	"""Return all the contents of the gedcom under this level 0 id (person id, family id, source id, ...)."""
	rec = gedcom.get_record(xref)
	if rec is None: return ""
	text = str(rec) + "\n"
	for sub_rec in rec.all_sub_rec_recursive():
		text += str(sub_rec) + "\n"
	return text

class GedcomProperties(NamedTuple):
	file_name: str
	file_directory: str
	records: int
	families: int
	people: int
	objects: int
	repositories: int
	shared_notes: int
	sources: int
	submitters: int
	others: int

def get_gedcom_properties(parser: Gedcom, gedcom_file: Path) -> GedcomProperties:
	counts = {"FAM":0, "INDI":0, "OBJE":0, "REPO":0, "SNOTE":0, "SOUR":0, "SUBM":0, None:0}
	for record in parser:
		if record.payload in counts.keys(): counts[record.payload] +=1
		else: counts[None] += 1
	return GedcomProperties(
		file_name = gedcom_file.name,
		file_directory = gedcom_file.resolve().parent.as_posix(),
		records = sum(counts.values()),
		families = counts["FAM"],
		people = counts["INDI"],
		objects = counts["OBJE"],
		repositories = counts["REPO"],
		shared_notes = counts["SNOTE"],
		sources = counts["SOUR"],
		submitters = counts["SUBM"],
		others = counts[None])

