from datetime import datetime, timedelta

from fastgedcom.base import Record
from fastgedcom.helpers import (
    DateType, extract_int_year, get_date_type, to_datetime, to_datetime_range
)
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")

person = next(document >> "INDI")
print("Age of", person.tag)

NUMBER_DAYS_PER_YEAR = 365.2425


###############################################################################
# Rough age (based years)
###############################################################################

def age_roughly(person: Record) -> float | None:
    birth_year = extract_int_year((person > "BIRT") >= "DATE")
    if birth_year is None:
        return None
    death_year = extract_int_year((person > "DEAT") >= "DATE")
    if death_year is None:
        if person > "DEAT":
            return None
        death_year = datetime.now().year
    return death_year - birth_year


print("Age (roughly):", age_roughly(person))


###############################################################################
# Precise age - best case (no date modifier)
###############################################################################

def age_precise_best_case(person: Record) -> timedelta | None:
    """Return the age of the given person, or return None
    when the age can't be computed.

    This function uses the :py:func:`to_datetime` function. Therefore, it
    raises ValueError for negative dates (BC or BCE)

    About modifiers, this function can handle ABT, CAL, or EST modifiers,
    but it will raise errors for modifiers like BET - AND or BEF.
    """
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
    """Return the age of the given person, or return None when
    the age can't be computed.

    This functions accepts negative dates (but isn't precise for those),
    and most date modifiers including BET - AND, BEF and AFT.
    """
    birth = (person > "BIRT") >= "DATE"
    death = (person > "DEAT") >= "DATE"

    # Preliminary study based on the year to handle negative dates
    birth_year = extract_int_year(birth)
    death_year = extract_int_year(death)
    if death_year is None and not person > "DEAT":
        death_year = datetime.now().year
    if birth_year is None or death_year is None:
        # Here, None stand here for "Unparsable date"
        return None
    if birth_year <= 0 or death_year <= 0:
        # Datetime doesn't accept negative dates
        # Assume comparing year is enough for BCE dates.
        return timedelta(days=int(NUMBER_DAYS_PER_YEAR*(death_year - birth_year)))

    # Look at the date modifier to either use to_datetime or to_datetime_range
    def convert_to_datetime(date_str: str) -> datetime:
        date_type = get_date_type(date_str)
        try:
            if date_type is None:
                # Here, None stand for "No modifier"
                date = to_datetime(birth)
            elif date_type in (DateType.ABT, DateType.CAL, DateType.EST):
                date = to_datetime(birth)
            elif date_type == DateType.BET_AND:
                date1, date2 = to_datetime_range(birth)
                date = date1 + (date2 - date1) / 2
            else:
                date = datetime(int(birth_year), 1, 1)
        except ValueError:
            date = datetime(int(birth_year), 1, 1)
        return date

    birth_date = convert_to_datetime(birth)
    if not person > "DEAT":
        death_date = datetime.now()
    else:
        death_date = convert_to_datetime(death)
    return death_date - birth_date


age_precise_general_case_ = age_precise_general_case(person)
if age_precise_general_case_ is None:
    print("Age (precise - general case):", None)
else:
    print("Age (precise - general case):",
          round(age_precise_general_case_.days / NUMBER_DAYS_PER_YEAR, 1))
