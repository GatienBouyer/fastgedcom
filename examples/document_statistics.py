from collections import defaultdict

from fastgedcom.base import Document, TrueLine
from fastgedcom.helpers import get_all_sub_lines
from fastgedcom.parser import strict_parse

document = strict_parse("../my_gedcom.ged")


###############################################################################
# Number of records
###############################################################################

nb_records_per_type: dict[str, int] = defaultdict(int)
for record in document:
	nb_records_per_type[record.payload] += 1

print("Number of level 0 lines:", sum(nb_records_per_type.values()))
print("Number of individuals:", nb_records_per_type["INDI"])
print("Number of families:", nb_records_per_type["FAM"])


###############################################################################
# Average number of lines
###############################################################################

if nb_records_per_type["INDI"] != 0:
	total_nb_lines_indi = 0
	for indi in document >> "INDI":
		total_nb_lines_indi += sum(1 for _ in get_all_sub_lines(indi))
	print("Average number of lines per INDI record:",
		total_nb_lines_indi / nb_records_per_type["INDI"])


###############################################################################
# Statistics on field hierarchy
###############################################################################

def get_field_usage(document: Document) -> dict[tuple[str, ...], int]:
	field_usage: dict[tuple[str, ...], int] = defaultdict(int)
	def recursion(line: TrueLine, tag_path: tuple[str, ...]) -> None:
		tag_path = *tag_path, line.tag
		field_usage[tag_path] += 1
		for sub_line in line.sub_lines:
			recursion(sub_line, tag_path)
	for record in document:
		if record.tag in ("HEAD","TRLR"): continue
		if record.payload == "SUBM": continue
		tag_path = (record.payload.split()[0],)
		field_usage[tag_path] += 1
		for line in record.sub_lines:
			recursion(line, tag_path)
	return field_usage

field_usage = get_field_usage(document)
sorted_field_usage = sorted(field_usage.items(), key=lambda i: i[1])
print("The 3 least present fields with their number of occurences:",
	*{("/".join(field), usage) for field, usage in sorted_field_usage[:3]})
