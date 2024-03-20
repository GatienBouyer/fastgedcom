from fastgedcom.parser import parse

file_pathname = "./my_new_gedcom.ged"

minimal_gedcom_text = """0 HEAD
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 TRLR
"""

minimal_gedcom, _ = parse(minimal_gedcom_text.splitlines())

gedcom_to_save = minimal_gedcom.get_source()

# Gedcom standards recommends the UTF-8 with BOM encoding for new gedcom.
with open(file_pathname, "w", encoding="utf-8-sig") as f:
    f.write(gedcom_to_save)
