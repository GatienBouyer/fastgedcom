from fastgedcom.base import FakeLine, IndiRef, Record, is_true
from fastgedcom.family_aid import FamilyAid
from fastgedcom.helpers import extract_int_year, extract_year, format_name
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")
booster = FamilyAid(document)

###############################################################################
# Iterate on individuals
###############################################################################

print("Longest name:",
	max((indi >= "NAME" for indi in document.get_records("INDI")), key=len))

###############################################################################
# Iterate on all records
###############################################################################

print("Number of records:", sum(1 for _ in iter(document)))

###############################################################################
# Iterate on parents
###############################################################################

def nb_ancestral_gen(indi: Record | FakeLine) -> int:
	if not is_true(indi): return 1
	father, mother = booster.get_parents(indi.tag)
	return 1+max(nb_ancestral_gen(father), nb_ancestral_gen(mother))

root = next(document.get_records("INDI"))
number_generations_above_root = nb_ancestral_gen(root)

print(f"Number of ascending generations from {format_name(root >= 'NAME')}:",
	number_generations_above_root)


###############################################################################
# Iterate on children
###############################################################################

def nb_of_descendants(indi: IndiRef, visited: set[IndiRef]) -> int:
	visited.add(indi)
	children = booster.get_children_ref(indi)
	return len(children) + sum(nb_of_descendants(c, visited) for c in children if c not in visited)

max_nb_desc = max(nb_of_descendants(indi.tag, set()) for indi in document.get_records("INDI"))
print("Maximum number of descendants:", max_nb_desc)


###############################################################################
# Iterate on people's age
###############################################################################

oldest = next(document.get_records("INDI"))
age_oldest = 0.0
for individual in document.get_records("INDI"):
	birth_date = (individual > "BIRT") >= "DATE"
	death_date = (individual > "DEAT") >= "DATE"
	birth_year = extract_int_year(birth_date)
	death_year = extract_int_year(death_date)
	if birth_year is None or death_year is None: continue
	age = death_year - birth_year
	if age > age_oldest:
		oldest = individual
		age_oldest = age

print("Oldest person:", format_name(oldest >= "NAME"))
print("His year of birth:", extract_year((oldest > "BIRT") >= "DATE"))
print("His year of death:", extract_year((oldest > "DEAT") >= "DATE"))
print("His age:", age_oldest)
