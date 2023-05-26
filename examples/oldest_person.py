from fastgedcom.helpers import (extract_int_year, extract_year, format_name,
                                get_source_infos)
from fastgedcom.parser import guess_encoding, parse

gedcom_file = "../my_gedcom.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	document, _ = parse(f)

oldest = next(document.get_records("INDI"))
age_oldest = 0.0 # the age is a float to handle all type of date
# A date such as" between 2001 and 2002" would by 2001.5
for individual in document.get_records("INDI"):
	birth_date = (individual > "BIRT") >= "DATE"
	death_date = (individual > "DEAT") >= "DATE"
	birth_year = extract_int_year(birth_date)
	death_year = extract_int_year(death_date)
	if birth_year is None or death_year is None: continue
	age = death_year - birth_year
	if age > age_oldest:
		oldest = individual
		age_oldest = age

print("Oldest person:", format_name(oldest >= "NAME"))
print("Year of birth:", extract_year((oldest > "BIRT") >= "DATE"))
print("Year of death:", extract_year((oldest > "DEAT") >= "DATE"))
print("Age:", age_oldest)
print("All the information:", get_source_infos(oldest))
