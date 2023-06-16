from fastgedcom.family_link import FamilyLink
from fastgedcom.helpers import format_name
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")
linker = FamilyLink(document)

person_id = next(document >> "INDI").tag

###############################################################################
# Usage of FamilyLink.get_relatives()
###############################################################################

parents = linker.get_relatives(person_id, 1)
grandparents = linker.get_relatives(person_id, 2)
grandchildren = linker.get_relatives(person_id, -2)

siblings = linker.get_relatives(person_id, 0, 1)
cousins = linker.get_relatives(person_id, 0, 2)
second_cousins = linker.get_relatives(person_id, 0, 3)

siblings_of_parents = linker.get_relatives(person_id, 1, 1)
oncles_and_aunts = siblings_of_parents
siblings_of_grandparents = linker.get_relatives(person_id, 2, 1)
cousins_of_parents = linker.get_relatives(person_id, 1, 2)

children_of_siblings = linker.get_relatives(person_id, -1, 1)
nephews_and_nieces = children_of_siblings
grandchildren_of_siblings = linker.get_relatives(person_id, -2, 1)
children_of_cousins = linker.get_relatives(person_id, -1, 2)


###############################################################################
# Usage of FamilyLink.traverse()
###############################################################################

parents = linker.traverse(person_id, 1)
grandparents = linker.traverse(person_id, 2)
grandchildren = linker.traverse(person_id, 0, 2)

siblings = linker.traverse(person_id, 1, 1)
cousins = linker.traverse(person_id, 2, 2)
second_cousins = linker.traverse(person_id, 3, 3)

oncles_and_aunts = linker.traverse(person_id, 2, 1)
nephews_and_nieces = linker.traverse(person_id, 1, 2)


###############################################################################
# Usage of FamilyLink.get_by_degree()
###############################################################################

person_name = format_name(document[person_id] >= 'NAME')

print(f"People with a kinship degree of 3 with {person_name},",
	"i.e. nieces and nephews, aunts and uncles,"
	"great-grandparents, and great-grandchildren:"
)

print(", ".join(
	format_name(p >= "NAME") for p in linker.get_by_degree(person_id, 3)
))
