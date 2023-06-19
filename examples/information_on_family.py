from fastgedcom.helpers import (extract_name_parts, extract_year, format_date,
                                format_name)
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")

family = next(document >> "FAM")
print("Information about", family.tag)

###############################################################################
# Family members
###############################################################################

# prehemptive check
husban_id = family >= "HUSB"
if husban_id in document:
	husban = document.records[husban_id]
	print("Husban is", format_name(husban >= "NAME"))

# after check, using FakeLine
wife_id = family >= "WIFE"
wife = document[wife_id]
if wife:
	print("Wife is", format_name(wife >= "NAME"))

# no check, assuming the records exists (could raise KeyError)
children_ids = [line.payload for line in family >> "CHIL"]
children = [document.records[child_id] for child_id in children_ids]
for k, child in enumerate(children):
	first_name, surname = extract_name_parts(child >= "NAME")
	birth_year = extract_year((child > "BIRT") >= "DATE")
	print(f"Child n°{k} is {first_name} born in {birth_year}")


###############################################################################
# Marriage
###############################################################################

if family > "MARR":
	date = (family > "MARR") >= "DATE"
	if date: print("Marriage date:", format_date(date))
	place = (family > "MARR") >= "PLAC"
	if place: print("Marriage place:", place)


###############################################################################
# Events
###############################################################################

if family > "DIV":
	print("They divorced")

for event in family >> "EVEN":
	print("Event:", event >= 'TYPE')


###############################################################################
# Raw gedcom information
###############################################################################

from fastgedcom.helpers import get_source

print("Original gedcom data:")
print(get_source(family))

