from fastgedcom.parser import strict_parse
from fastgedcom.helpers import format_date

document = strict_parse("../my_gedcom.ged")

birth_date = (document["@I1@"] > "BIRT") >= "DATE"
print(format_date(birth_date))


from fastgedcom.base import is_true

indi = document["@I13@"]
if not (indi > "DEAT"): # Not compliant with type checkers
	print("No DEAT field. The person is alive")
if not is_true(indi > "DEAT"): # Compliant with type checkers
	print("No DEAT field. The person is alive")
else: # Can continue anyway
	print("Death date:", format_date((indi > "DEAT") >= "DATE"))