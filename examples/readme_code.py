from fastgedcom.parser import strict_parse
from fastgedcom.helpers import format_date

document = strict_parse("../my_gedcom.ged")

birth_date = (document["@I1@"] > "BIRT") >= "DATE"
print(format_date(birth_date))


indi = document["@I13@"]
death = indi > "DEAT"
if not death:
	print("No DEAT field. The person is alive")
# Can continue anyway
print("Death date:", format_date(death >= "DATE"))
