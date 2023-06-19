from time import perf_counter

from gedcom import parse_fp, Individual

gedcom_file = "../my_gedcom.ged"

start_time = perf_counter()

with open(gedcom_file, "r", encoding="utf-8-sig") as f:
	gedcom = parse_fp(f)

end_time = perf_counter()

print(f"Time to parse: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_gen(indi: Individual) -> int:
	return max([1+nb_gen(p) for p in indi.parents] + [1])

number_generations_above_root = nb_gen(gedcom["@I1@"])

end_time = perf_counter()

print(f"Number of generations above root: {number_generations_above_root}")
print(f"Time to traverse parents: {end_time - start_time}")

##############################################################################

start_time = perf_counter()

def nb_descendants_rec(parent: Individual) -> int:
	children = []
	for fam in parent.child_elements:
		if fam.tag != "FAMS": continue
		for e in gedcom[fam.value].child_elements:
			if e.tag == "CHIL": children.append(gedcom[e.value])
	return len(children) + sum(nb_descendants_rec(child) for child in children)


nb_descendants = nb_descendants_rec(gedcom["@I1692@"])

end_time = perf_counter()

print(f"Number of children: {nb_descendants}")
print(f"Time to traverse children: {end_time - start_time}")


##############################################################################

from fastgedcom.helpers import extract_int_year

start_time = perf_counter()

oldest = next(gedcom.individuals)
age_oldest = 0.0
for individual in gedcom.individuals:
	try:
		birth_date = individual.birth.date
		death_date = individual.death.date
	except IndexError:
		continue
	birth_year = extract_int_year(birth_date)
	death_year = extract_int_year(death_date)
	if birth_year is None or death_year is None: continue
	age = death_year - birth_year
	if age > age_oldest:
		oldest = individual
		age_oldest = age

end_time = perf_counter()

print(f"Oldest person: {oldest.name}    Age: {age_oldest}")
print(f"Time to traverse ages: {end_time - start_time}")
