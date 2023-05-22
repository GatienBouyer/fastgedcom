from fastgedcom.gedcom_parser import guess_encoding, parse

gedcom_file = "C:/Users/gatie/Documents/Scripts_Python/GeneaCharts/bouyer-perret 20220809.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	gedcom, warnings = parse(f)
print("Warnings:", *warnings, sep="\n", end="---\n")

indi = gedcom.get_record("@I1@")
assert(indi)
name = indi.get_sub_record_payload("NAME")
print(name)
