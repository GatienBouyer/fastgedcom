from fastgedcom.base import FakeLine, TrueLine, is_true
from fastgedcom.family_aid import FamilyAid
from fastgedcom.parser import strict_parse

gedcom_file = "../my_gedcom.ged"
document = strict_parse(gedcom_file)

booster = FamilyAid(document)
def nb_ancestral_gen(indi: TrueLine | FakeLine) -> int:
	if not is_true(indi): return 1
	father, mother = booster.get_parents(indi.tag)
	return 1+max(nb_ancestral_gen(father), nb_ancestral_gen(mother))

number_generations_above_root = nb_ancestral_gen(document["@I1@"])

print(f"Number of generations above root: {number_generations_above_root}")
