from fastgedcom.base import FakeLine, IndiRef, Record, is_true
from fastgedcom.family_link import FamilyLink
from fastgedcom.helpers import format_name
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")
families = FamilyLink(document)

###############################################################################
# Iterate on individuals
###############################################################################

print("Longest name:",
	max((indi >= "NAME" for indi in document >> "INDI"), key=len))

###############################################################################
# Iterate on all records
###############################################################################

print("Number of records:", sum(1 for _ in iter(document)))

###############################################################################
# Iterate on parents
###############################################################################

def nb_ancestral_gen(indi: Record | FakeLine) -> int:
	if not is_true(indi): return 1
	father, mother = families.get_parents(indi.tag)
	return 1+max(nb_ancestral_gen(father), nb_ancestral_gen(mother))

root = next(document >> "INDI")
number_generations_above_root = nb_ancestral_gen(root)

print(f"Number of ascending generations from {format_name(root >= 'NAME')}:",
	number_generations_above_root)


###############################################################################
# Iterate on children
###############################################################################

def nb_of_descendants(indi: IndiRef, visited: set[IndiRef]) -> int:
	visited.add(indi)
	children = families.get_children_ref(indi)
	return len(children) + sum(nb_of_descendants(c, visited)
		for c in children if c not in visited)

max_nb_desc = max(nb_of_descendants(indi.tag, set()) for indi in document >> "INDI")
print("Maximum number of descendants:", max_nb_desc)


