from fastgedcom.helpers import (
    extract_name_parts, extract_year, format_date, format_name
)
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")

family = next(document >> "FAM")
print("Information about", family.tag)

###############################################################################
# Family members
###############################################################################

husband_id = family >= "HUSB"
if husband_id in document:
    husband = document.records[husband_id]
    print("Husband is", format_name(husband >= "NAME"))

wife = document[family >= "WIFE"]
if wife:  # would be a fake line if the wife isn't in the document
    print("Wife is", format_name(wife >= "NAME"))

children_ids = [line.payload for line in family >> "CHIL"]
for k, child_id in enumerate(children_ids):
    child = document[child_id]  # assume that the child is defined, otherwise raise KeyError
    first_name, surname = extract_name_parts(child >= "NAME")
    birth_year = extract_year((child > "BIRT") >= "DATE")
    print(f"Child n°{k} is {first_name} born in {birth_year}")


###############################################################################
# Marriage
###############################################################################

if family > "MARR":
    date = (family > "MARR") >= "DATE"
    if date:
        print("Marriage date:", format_date(date))
    place = (family > "MARR") >= "PLAC"
    if place:
        print("Marriage place:", place)


###############################################################################
# Events
###############################################################################

if family > "DIV":
    print("They divorced")

for event in family >> "EVEN":
    print("Event:", event >= 'TYPE')
