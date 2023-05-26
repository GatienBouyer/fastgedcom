from fastgedcom.parser import guess_encoding, parse

gedcom_file = "my_gedcom_file.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	document, warnings = parse(f)

print(warnings) # in case of duplicate record reference

from fastgedcom.helpers import format_date

birth_date = (document["@I1@"] > "BIRT") >= "DATE"
print(format_date(birth_date))

from fastgedcom.base import is_true

indi = document["@I1"]
death_date = (indi > "DEAT") >= "DATE"
if death_date != "": print(format_date(death_date)) 
if not is_true(indi): print("It was not even present!")

indi = document.get_record("@I1@")
surname = indi.get_sub_line("NAME").get_sub_line_payload("SURN")

from fastgedcom.base import Document, FakeLine, IndiRef, Record, is_true
from fastgedcom.helpers import format_name


def print_infos(gedcom: Document, indi: IndiRef) -> None:
	record = gedcom[indi]
	if is_true(record): print_name(record)

def print_name(record: Record | FakeLine) -> None:
	print(format_name(record >= "NAME"))

print_infos(document, "@I1@")

from fastgedcom.family_aid import FamilyAid

booster = FamilyAid(document)

def number_of_ascendants(indi: Record | FakeLine) -> int:
	if not is_true(indi): return 1
	father, mother = booster.get_parents(indi.tag)
	return 1+max(number_of_ascendants(father), number_of_ascendants(mother))

def number_of_descendants(indi: IndiRef) -> int:
	children = booster.get_children(indi)
	return len(children) + sum(number_of_descendants(c) for c in children)

print(number_of_ascendants(document["@I1@"]))
print(number_of_descendants("@I1@"))
