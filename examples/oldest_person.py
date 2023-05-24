from fastgedcom.helpers import (extract_int_year, extract_year, format_name,
                                get_gedcom_source)
from fastgedcom.parser import guess_encoding, parse

gedcom_file = "C:/Users/gatie/Documents/Scripts_Python/GeneaCharts/bouyer-perret 20220809.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	gedcom, _ = parse(f)

oldest = next(gedcom.get_records("INDI")).tag
age_oldest = 0.0 # the age is a float to handle all type of date
# A date such as between 2001 and 2002 returns 2001.5
for individual in gedcom.get_records("INDI"):
	birth_date = (gedcom[individual.tag] > "BIRT") >= "DATE"
	death_date = (gedcom[individual.tag] > "DEAT") >= "DATE"
	birth_year = extract_int_year(birth_date)
	death_year = extract_int_year(death_date)
	if birth_year is None or death_year is None: continue
	age = death_year - birth_year
	if age > age_oldest:
		oldest = individual.tag
		age_oldest = age

print("Oldest person:", format_name(gedcom[oldest] >= "NAME"))
print("Year of birth:", extract_year((gedcom[oldest] > "BIRT") >= "DATE"))
print("Year of death:", extract_year((gedcom[oldest] > "DEAT") >= "DATE"))
print("Age:", age_oldest)
print("All the information:", get_gedcom_source(gedcom[oldest]))
