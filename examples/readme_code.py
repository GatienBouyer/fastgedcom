from fastgedcom.base import FakeLine, Record
from fastgedcom.family_link import FamilyLink
from fastgedcom.helpers import extract_name_parts
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")
person = document["@I1@"]
# use ">" to get a sub-line
death = person > "DEAT"
# use ">=" to get a sub-line value
date = death >= "DATE"
print(date)
# Prints "" if the field is missing


##############################################################################


document = strict_parse("../my_gedcom.ged")

person = document["@I1@"]
name = person >= "NAME"
print(name)  # Unformatted string such as "John /Doe/"

given_name, surname = extract_name_parts(name)
print(f"{given_name.capitalize()} {surname.upper()}")  # Would be "John DOE"

alias = person > "NAME" >= "_AKA"
print(f"a.k.a: {alias}")  # Could be "Johnny" or ""


##############################################################################


indi = document["@I13@"]

# You can access the date of death, whether the person is deceased or not.
date = (indi > "DEAT") >= "DATE"

# The date of death or an empty string
print("Death date:", date)


##############################################################################


for indi in document:
    line = indi > "_UID"
    if line:  # Check if field _UID exists to avoid ValueError in list.remove()
        indi.sub_lines.remove(line)

# Get the Document as a gedcom string to write it into a file
gedcom_without_uids = document.get_source()

with open("./gedcom_without_uids.ged", "w", encoding="utf-8-sig") as f:
    f.write(gedcom_without_uids)


##############################################################################


# For fast and easy family lookups
families = FamilyLink(document)


def nb_anc_gen(indi: Record | FakeLine) -> int:
    """Return the count of ancestral generation of the given person."""
    if not indi:
        return 1
    father, mother = families.get_parents(indi.tag)
    return 1+max(nb_anc_gen(father), nb_anc_gen(mother))


root = document["@I1@"]
number_generations_above_root = nb_anc_gen(root)
