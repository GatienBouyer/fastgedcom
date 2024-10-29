from fastgedcom.helpers import extract_name_parts, format_date, format_name
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
    # assume that the child is defined, otherwise the next line will raise KeyError
    child = document[child_id]
    first_name, surname = extract_name_parts(child >= "NAME")
    print(f"Child n°{k} is {first_name}")

# For extensive lookups of parents and/or children, see fastgedcom.family_link

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
