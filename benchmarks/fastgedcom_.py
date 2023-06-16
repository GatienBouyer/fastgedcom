from time import perf_counter

from fastgedcom.base import FakeLine, IndiRef, Record
from fastgedcom.family_link import FamilyLink
from fastgedcom.helpers import extract_int_year, format_name
from fastgedcom.parser import strict_parse

gedcom_file = "../my_gedcom.ged"

start_time = perf_counter()

gedcom = strict_parse(gedcom_file)
families = FamilyLink(gedcom)

end_time = perf_counter()

print(f"Time to parse: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_gen(indi: Record | FakeLine) -> int:
	if not indi: return 1
	father, mother = families.get_parents(indi.tag)
	return 1+max(nb_gen(father), nb_gen(mother))

number_generations_above_root = nb_gen(gedcom["@I1@"])

end_time = perf_counter()

print(f"Number of generations above root: {number_generations_above_root}")
print(f"Time to traverse parents: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_descendants_rec(parent: IndiRef) -> int:
	children = families.get_children_ref(parent)
	return len(children) + sum(nb_descendants_rec(child) for child in children)

nb_descendants = nb_descendants_rec("@I1692@")

end_time = perf_counter()

print(f"Number of children: {nb_descendants}")
print(f"Time to traverse children: {end_time - start_time}")


##############################################################################

start_time = perf_counter()

oldest = next(gedcom.get_records("INDI"))
age_oldest = 0.0
for individual in gedcom.get_records("INDI"):
	birth_year = extract_int_year((individual > "BIRT") >= "DATE")
	death_year = extract_int_year((individual > "DEAT") >= "DATE")
	if birth_year is None or death_year is None: continue
	age = death_year - birth_year
	if age > age_oldest:
		oldest = individual
		age_oldest = age

end_time = perf_counter()

print(f"Oldest person: {format_name(oldest >= 'NAME')}    Age: {age_oldest}")
print(f"Time to traverse ages: {end_time - start_time}")
