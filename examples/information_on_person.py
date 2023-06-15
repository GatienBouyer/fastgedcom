from datetime import datetime

from fastgedcom.base import IndiRef, Record
from fastgedcom.helpers import (extract_int_year, extract_name_parts,
                                format_date, format_name, get_all_sub_lines,
                                line_to_datetime)
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")

person = next(document >> "INDI")
person_id = person.tag
print("Information about", person_id)


###############################################################################
# Standard informations on the person itself
###############################################################################

print("Full name:", format_name(person >= "NAME"))
print("Lastname:", (person > "NAME") >= "SURN")
print("Firstname(s):", (person > "NAME") >= "GIVN")

print("Gender:", person >= "SEX")

if person > "BIRT":
	print("Birth date:", format_date((person > "BIRT") >= "DATE"))
	print("Birth place:", (person > "BIRT") >= "PLAC")

if person > "DEAT":
	print("Death date:", format_date(((person) > "DEAT") >= "DATE"))
	print("Death place:", (person > "DEAT") >= "PLAC")
else:
	print("Alive: yes")


birth_year = extract_int_year((person > "BIRT") >= "DATE")
if birth_year is not None:
	death_year: int | float | None
	if not person > "DEAT":
		death_year = datetime.now().year
	else:
		death_year = extract_int_year((person > "DEAT") >= "DATE")
	if death_year is not None:
		print("Age:", death_year - birth_year)


###############################################################################
# Additional informations on the person itself
###############################################################################

if person > "NOTE":
	print("Note:", (person > "NOTE").payload_with_cont)

if person > "CHR":
	# Note that several other tags exist for religious events
	print("Christening: yes")

if person > "SOUR":
	for source in person >> "SOUR":
		print("Information source:", ", ".join(
			addr.payload for addr in get_all_sub_lines(source)))

if person > "CHAN":
	last_change = line_to_datetime((person > "CHAN") > "DATE")
	print("Last update:", last_change)


###############################################################################
# Familial informations - person's close relatives
###############################################################################

from fastgedcom.family_link import FamilyLink

linker = FamilyLink(document)

father, mother = linker.get_parents(person_id)
if father: print("Father:", format_name(father >= "NAME"))
else: print("Unknown father")
if mother: print("Mother:", format_name(mother >= "NAME"))
else: print("Unknown mother")


mother_firstname, mother_family_name = extract_name_parts(mother >= "NAME")
# could also use the payload of ((mother > "NAME") >= "SURN") if defined
print("Mother's maiden name:", mother_family_name)

print("Siblings:", ", " .join(
	(p > "NAME") >= "GIVN" for p in linker.get_siblings(person_id)
))

print("Stepsiblings:", ", ".join(
	format_name(p >= "NAME") for p in linker.get_stepsiblings(person_id)
))

print("Spouse(s):", ", ".join(
	format_name(p >= "NAME") for p in linker.get_spouses(person_id)
))

children = linker.get_children(person_id)
children.sort(key=lambda c:
	extract_int_year((c > "BIRT") >= "DATE", default=999)
)
print("Children:", ", ".join(
	(child > "NAME") >= "GIVN" for child in children
))



###############################################################################
# Familial informations - person's distant relatives
###############################################################################

def get_cousins(person_id: IndiRef) -> list[Record]:
	cousins = []
	for parent in linker.get_parents(person_id):
		if parent.exists is False: continue
		for sibling_ref in linker.get_all_siblings_ref(parent.tag):
			cousins.extend(linker.get_children(sibling_ref))
	return cousins

print("Cousins:", ", ".join(
	(c > "NAME") >= "GIVN" for c in get_cousins(person_id)
))

