from time import perf_counter

from fastgedcom.helpers import extract_int_year, format_name
from pygedcom import GedcomParser
from pygedcom.elements.rootElements.individual import GedcomIndividual

gedcom_file = "../my_gedcom.ged"

start_time = perf_counter()

gedcom = GedcomParser(path=gedcom_file)
gedcom.parse()

end_time = perf_counter()

print(f"Time to parse: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_gen(indi: GedcomIndividual) -> int:
	return max([1+nb_gen(p) for p in gedcom.get_parents(indi)] + [1])

number_generations_above_root = nb_gen(gedcom.find_individual("@I1@"))

end_time = perf_counter()

print(f"Number of generations above root: {number_generations_above_root}")
print(f"Time to traverse parents: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_descendants_rec(parent: GedcomIndividual) -> int:
	children = gedcom.get_children(parent)
	return len(children) + sum(nb_descendants_rec(child) for child in children)


nb_descendants = nb_descendants_rec(gedcom.find_individual("@I1692@"))

end_time = perf_counter()

print(f"Number of children: {nb_descendants}")
print(f"Time to traverse children: {end_time - start_time}")


##############################################################################

start_time = perf_counter()

oldest = gedcom.individuals[0]
age_oldest = 0.0
for individual in gedcom.individuals:
	birth_date = individual.get_birth().get_date().get_value()
	death_date = individual.get_death().get_date().get_value()
	birth_year = extract_int_year(birth_date)
	death_year = extract_int_year(death_date)
	if birth_year is None or death_year is None: continue
	age = death_year - birth_year
	if age > age_oldest:
		oldest = individual
		age_oldest = age

end_time = perf_counter()

print(f"Oldest person: {format_name(oldest.get_name())}    Age: {age_oldest}")
print(f"Time to traverse ages: {end_time - start_time}")
