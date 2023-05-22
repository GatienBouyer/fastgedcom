from fastgedcom.gedcom_parser import guess_encoding, parse
from fastgedcom.gedcom_structure import IndiRef

gedcom_file = "C:/Users/gatie/Documents/Scripts_Python/GeneaCharts/bouyer-perret 20220809.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	gedcom, _ = parse(f)

def nb_ancestral_gen(indi: IndiRef) -> int:
	father, mother = gedcom.get_parents(indi)
	father_gens = 0 if father is None else 1+nb_ancestral_gen(father)
	mother_gens = 0 if mother is None else 1+nb_ancestral_gen(mother)
	return max(1, father_gens, mother_gens)

number_generations_above_root = nb_ancestral_gen("@I1@")

print(f"Number of generations above root: {number_generations_above_root}")
