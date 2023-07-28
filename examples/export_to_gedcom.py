from fastgedcom.base import Document
from fastgedcom.helpers import get_source
from fastgedcom.parser import parse

file_pathname = "../my_new_gedcom.ged"

minimal_gedcom_text = """0 HEAD
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 TRLR
"""
minimal_gedcom, _ = parse(minimal_gedcom_text.splitlines())


def save(document: Document) -> str:
	text = ""
	for record in document:
		record_gedcom = get_source(record)
		text += record_gedcom
	return text

gedcom_to_save = save(minimal_gedcom)

assert(gedcom_to_save == minimal_gedcom_text)

# Gedcom standards recommends the UTF-8 with BOM encoding for new gedcom.
with open(file_pathname, "w", encoding="utf-8-sig") as f:
	f.write(gedcom_to_save)
