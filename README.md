# FastGedcom

A gedcom tool to parse, browse and modify gedcom files


## Installation
You can install FastGedcom using pip:
```bash
pip install fastgedcom
```

The `ansel` library is a dependancy of FastGedcom. It is automatically installed by pip. This library allows to decode files encoded in ansel or gedcom.


## Features

- Supports the read of gedcom files encoded in UTF-8 with and without BOM, UTF-16 (also named UNICODE), ANSI, and ANSEL.
- ~~Supports the export to gedcom files encoded in UTF-8, UTF-16, and ANSI.~~

- The gedcom representation (the data structure) is very lite (2 classes overall).
- No data parsing is done (due to the wide diversity), but helper methods are provided.


## Motivations

The FastGedcom library is intented to be read, understood, and used quickly, so you focus on what really matters. The code has type hints to help with development. Functions are based directly on gedcom pointers for ease of use. Due to the wide variety of gedcom software, no data parsing is done, but some standalone functions are provided (see the `fastgedcom.helpers` module).


## Usage examples

In the following example, we print the name of the person under the reference @I1@.
```python
from fastgedcom.parser import guess_encoding, parse

gedcom_file = YOUR_GEDCOM_FILE
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	gedcom, warnings = parse(f)
print("Warnings: ", *warnings, sep="\n", end="---\n")

indi = gedcom.get_record("@I1@")
surname = indi.get_sub_record("NAME").get_sub_record_payload("SURN")
print(surname)

# With magic methods:
print((gedcom["@I1@"] > "NAME") >= "SURN")
```

In the following example, we count the number of ancestral generations of the person whose reference is @I1@.
```python
from fastgedcom.parser import guess_encoding, parse
from fastgedcom.structure import IndiRef

gedcom_file = YOUR_GEDCOM_FILE
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	gedcom, _ = parse(f)

def nb_ancestral_gen(indi: IndiRef) -> int:
	father, mother = gedcom.get_parents(indi)
	father_gens = 0 if father is None else 1+nb_ancestral_gen(father)
	mother_gens = 0 if mother is None else 1+nb_ancestral_gen(mother)
	return max(1, father_gens, mother_gens)

number_generations_above_root = nb_ancestral_gen("@I1@")

print(f"Number of generations above root: {number_generations_above_root}")
```

In the following example, we find the oldest deceased person. Then, we print his name and all his gedcom information using the `fastgedcom.helpers` module
```python
from fastgedcom.helpers import (extract_int_year, extract_year, format_name,
                                get_gedcom_data)
from fastgedcom.parser import guess_encoding, parse

gedcom_file = YOUR_GEDCOM_FILE
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
print("All the information:", get_gedcom_data(gedcom, oldest))
```


## Contributing

Contributions are welcome, and they will be greatly appreciated!

If you like this project, consider putting a star on [Github](https://github.com/GatienBouyer/fastgedcom), thank you!

For any feedback or question, please feel free to contact me by email at gatien.bouyer.dev@gmail.com or via [Github issues](https://github.com/GatienBouyer/fastgedcom/issues).
