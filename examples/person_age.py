from datetime import datetime, timedelta

from fastgedcom.base import Record
from fastgedcom.helpers import extract_int_year, line_to_datetime, to_datetime
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
    birth = (person > "BIRT") > "DATE"
    death = (person > "DEAT") > "DATE"

    # Preliminary study based on the year to handle negative dates
    birth_year = extract_int_year(birth.payload)
    death_year = extract_int_year(death.payload)
    if death_year is None and not person > "DEAT":
        death_year = datetime.now().year
    if birth_year is None or death_year is None:
        # Here, None stand here for "Unparsable date"
        return None
    if birth_year <= 0 or death_year <= 0:
        # Datetime doesn't accept negative dates
        # Assume comparing year is enough for BCE dates.
        return timedelta(days=int(NUMBER_DAYS_PER_YEAR*(death_year - birth_year)))

    birth_date = line_to_datetime(birth, datetime(int(birth_year), 1, 1))
    if not person > "DEAT":
        death_date = datetime.now()
    else:
        death_date = line_to_datetime(death, datetime(int(death_year), 1, 1))
    return death_date - birth_date


age_precise_general_case_ = age_precise_general_case(person)
if age_precise_general_case_ is None:
    print("Age (precise - general case):", None)
else:
    print("Age (precise - general case):",
          round(age_precise_general_case_.days / NUMBER_DAYS_PER_YEAR, 1))
