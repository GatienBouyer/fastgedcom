from fastgedcom.helpers import (extract_int_year, extract_year, format_name,
                                get_source_infos)
from fastgedcom.parser import strict_parse

gedcom_file = "../my_gedcom.ged"
document = strict_parse(gedcom_file)

oldest = next(document.get_records("INDI"))
age_oldest = 0.0
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
