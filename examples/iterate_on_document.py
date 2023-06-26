from fastgedcom.base import FakeLine, IndiRef, Record
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

# Recursively
def nb_ancestral_gen(indi: Record | FakeLine) -> int:
	if not indi: return 1
	father, mother = families.get_parents(indi.tag)
	return 1+max(nb_ancestral_gen(father), nb_ancestral_gen(mother))

root = next(document >> "INDI")
number_generations_above_root = nb_ancestral_gen(root)

print(f"Number of ascending generations from {format_name(root >= 'NAME')}:",
	number_generations_above_root)

# Without recursion
def get_ascendants(root: IndiRef, max_gen: int) -> list[Record]:
	indis: list[tuple[int, Record]] = [(1, document.records[root])]
	ascendants: list[Record] = []
	for gen, indi in indis:
		if gen > max_gen: continue
		ascendants.append(indi)
		for parent in families.get_parents(indi.tag):
			if parent: indis.append((gen+1, parent))
	return ascendants

print(f"Number of ascendants of {format_name(root >= 'NAME')} until the 5th generation:",
	len(get_ascendants(root.tag, 5)))
print("For a complete genealogy on the 5 ascending generation,",
	"this number of ascendants should be:", sum(2**i for i in range(5)))


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


