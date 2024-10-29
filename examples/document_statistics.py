from collections import defaultdict
from collections.abc import Generator

from fastgedcom.base import Document, TrueLine
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
# Average number of lines per INDI record
###############################################################################

if nb_records_per_type["INDI"] != 0:
    total_nb_lines_indi = 0
    for indi in document >> "INDI":
        total_nb_lines_indi += sum(1 for _ in indi.get_all_sub_lines())
    print("Average number of lines per INDI record:",
          total_nb_lines_indi / nb_records_per_type["INDI"])


###############################################################################
# Statistics on the most common fields
###############################################################################

def get_field_usage(document: Document) -> dict[str, int]:
    field_usage: dict[str, int] = defaultdict(int)
    for record, *lines in document.all_lines():
        if record.tag in ("HEAD", "TRLR"):
            continue
        if record.payload == "SUBM":
            continue
        path_str = record.payload + "/" + "/".join(p.tag for p in lines)
        field_usage[path_str] += 1
    return field_usage


field_usage = get_field_usage(document)
sorted_field_usage = sorted(field_usage.items(), key=lambda elt: (elt[1], elt[0]))
print("The 3 least present fields with their number of occurences:",
      *[(field, usage) for field, usage in sorted_field_usage[:3]])
print("The 3 most present fields with their number of occurences:",
      *[(field, usage) for field, usage in sorted_field_usage[-3:]])
