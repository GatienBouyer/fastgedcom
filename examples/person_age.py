from datetime import datetime, timedelta

from fastgedcom.base import Record
from fastgedcom.helpers import (DateType, extract_int_year, get_date_type,
                                to_datetime, to_datetime_range)
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")

person = next(document >> "INDI")
print("Age of", person.tag)

NUMBER_DAYS_PER_YEAR = 365.2425


###############################################################################
# Rough age (based on the years)
###############################################################################

def age_roughly(person: Record) -> float| None:
	birth_year = extract_int_year((person > "BIRT") >= "DATE")
	if birth_year is None: return None
	death_year = extract_int_year((person > "DEAT") >= "DATE")
	if death_year is None:
		if person > "DEAT": return None
		death_year = datetime.now().year
	return death_year - birth_year

print("Age (roughly):", age_roughly(person))


###############################################################################
# Precise age - best case
###############################################################################

def age_precise_best_case(person: Record) -> timedelta | None:
	"""The best case is conditioned by the :py:func:`to_datetime` function.
	The best case is a positive year possibly with a :py:attr:`ABT`,
	:py:attr:`CAL` or :py:attr:`EST` modifier."""
	try:
		birth_date = to_datetime((person > "BIRT") >= "DATE")
		if person > "DEAT":
			death_date = to_datetime((person > "DEAT") >= "DATE")
		else:
			death_date = datetime.now()
	except ValueError:
		return None
	return death_date - birth_date

age_precise_best_case_ = age_precise_best_case(person)
if age_precise_best_case_ is None:
	print("Age (precise - best case):", None)
else:
	print("Age (precise - best case):",
		round(age_precise_best_case_.days / NUMBER_DAYS_PER_YEAR, 1))


###############################################################################
# Precise age - General case
###############################################################################

def age_precise_general_case(person: Record) -> timedelta | None:
	birth = (person > "BIRT") >= "DATE"
	death = (person > "DEAT") >= "DATE"
	birth_year = extract_int_year(birth)
	death_year = extract_int_year(death)
	if death_year is None and not person > "DEAT":
		death_year = datetime.now().year
	if birth_year is None or death_year is None:
		# Here, None stand here for "Unparsable date"
		return None
	if birth_year <= 0 or death_year <= 0: # datetime can't handle negative dates
		return timedelta(days=int(NUMBER_DAYS_PER_YEAR*(death_year - birth_year)))
	birth_date_type = get_date_type(birth)
	try:
		if birth_date_type is None: # Here, None stand for "No modifier"
			birth_date = to_datetime(birth)
		elif birth_date_type in (DateType.ABT, DateType.CAL, DateType.EST):
			birth_date = to_datetime(birth)
		elif birth_date_type == DateType.BET_AND:
			birth_date1, birth_date2 = to_datetime_range(birth)
			birth_date = birth_date1 + (birth_date2 - birth_date1) / 2
		else:
			birth_date = datetime(int(birth_year), 1, 1)
	except ValueError:
		birth_date = datetime(int(birth_year), 1, 1)
	if not person > "DEAT":
		death_date = datetime.now()
	else:
		death_date_type = get_date_type(death)
		try:
			if death_date_type is None:
				death_date = to_datetime(death)
			elif death_date_type in (DateType.ABT, DateType.CAL, DateType.EST):
				death_date = to_datetime(death)
			elif death_date_type == DateType.BET_AND:
				death_date1, death_date2 = to_datetime_range(death)
				death_date = death_date1 + (death_date2 - death_date1) / 2
			else:
				death_date = datetime(int(death_year), 1, 1)
		except ValueError:
			death_date = datetime(int(death_year), 1, 1)
	return death_date - birth_date

age_precise_general_case_ = age_precise_general_case(person)
if age_precise_general_case_ is None:
	print("Age (precise - general case):", None)
else:
	print("Age (precise - general case):",
		round(age_precise_general_case_.days / NUMBER_DAYS_PER_YEAR, 1))

