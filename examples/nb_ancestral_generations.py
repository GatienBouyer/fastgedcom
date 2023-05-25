from fastgedcom.base import IndiRef
from fastgedcom.family_aid import FamilyAid
from fastgedcom.parser import guess_encoding, parse

gedcom_file = "C:/Users/gatie/Documents/Scripts_Python/GeneaCharts/bouyer-perret 20220809.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	gedcom, _ = parse(f)

booster = FamilyAid(gedcom)
def nb_ancestral_gen(indi: IndiRef) -> int:
	father, mother = booster.get_parents(indi)
	father_gens = 0 if father is None else 1+nb_ancestral_gen(father)
	mother_gens = 0 if mother is None else 1+nb_ancestral_gen(mother)
	return max(1, father_gens, mother_gens)

number_generations_above_root = nb_ancestral_gen("@I1@")

print(f"Number of generations above root: {number_generations_above_root}")
