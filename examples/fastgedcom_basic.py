from fastgedcom.parser import guess_encoding, parse

gedcom_file = "C:/Users/gatie/Documents/Scripts_Python/GeneaCharts/bouyer-perret 20220809.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	document, warnings = parse(f)
print("Warnings: ", *warnings, sep="\n", end="---\n")

indi = document.get_record("@I1@")
surname = indi.get_sub_line("NAME").get_sub_line_payload("SURN")
print(surname)

# With magic methods:
print((document["@I1@"] > "NAME") >= "SURN")
