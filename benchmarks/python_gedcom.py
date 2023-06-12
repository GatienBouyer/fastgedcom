from time import perf_counter

from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser

gedcom_file = "../my_gedcom.ged"

start_time = perf_counter()

gedcom = Parser()
gedcom.parse_file(gedcom_file)

end_time = perf_counter()

print(f"Time to parse: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_gen(indi: IndividualElement) -> int:
	parents = gedcom.get_parents(indi)
	return max([1+nb_gen(p) for p in parents] + [1])

root = gedcom.get_element_dictionary()["@I1@"]
number_generations_above_root = nb_gen(root)

end_time = perf_counter()

print(f"Number of generations above root: {number_generations_above_root}")
print(f"Time to traverse parents: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_descendants_rec(parent: IndividualElement) -> int:
	children = [c for f in gedcom.get_families(parent)
		for c in gedcom.get_family_members(f, "CHIL")]
	return len(children) + sum(nb_descendants_rec(child) for child in children)


root2 = gedcom.get_element_dictionary()["@I1692@"]
nb_descendants = nb_descendants_rec(root2)

end_time = perf_counter()

print(f"Number of children: {nb_descendants}")
print(f"Time to traverse children: {end_time - start_time}")


##############################################################################

from fastgedcom.helpers import extract_int_year

start_time = perf_counter()

oldest: IndividualElement | None = None
age_oldest = 0.0
for element in gedcom.get_root_child_elements():
	if not isinstance(element, IndividualElement): continue
	birth_date, *_ = element.get_birth_data()
	death_date, *_ = element.get_death_data()
	birth_year = extract_int_year(birth_date)
	death_year = extract_int_year(death_date)
	if birth_year is None or death_year is None: continue
	age = death_year - birth_year
	if age > age_oldest:
		oldest = element
		age_oldest = age

end_time = perf_counter()
assert(oldest)
print(f"Oldest person: {oldest.get_name()}    Age: {age_oldest}")
print(f"Time to traverse ages: {end_time - start_time}")
