# FastGedcom

A lightweight tool to parse, browse and edit gedcom files.

```bash
pip install fastgedcom
```

Want to open a gedcom file?
```python
from fastgedcom.parser import guess_encoding, parse

gedcom_file = "my_gedcom_file.ged"
with open(gedcom_file, "r", encoding=guess_encoding(gedcom_file)) as f:
	document, warnings = parse(f)

if warnings: print(warnings) # in case of duplicate record reference
```


Easy to write! Free choice of fields, data, and formatting.
```python
from fastgedcom.helpers import format_date

birth_date = (document["@I1@"] > "BIRT") >= "DATE"
print(format_date(birth_date))
```

A field is missing? FakeLine to the rescue. Like a TrueLine, but no error, no value, and no error handling code!
```python
from fastgedcom.base import is_true

indi = document["@I1@"]
death_date = (indi > "DEAT") >= "DATE"
if death_date != "": print(format_date(death_date)) 
if not is_true(indi): print("It was not even present!")
```

Don't like magic operator overload? Use standard methods!
```python
indi = document.get_record("@I1@")
surname = indi.get_sub_line("NAME").get_sub_line_payload("SURN")
```

Typehints for salvation! Autocompletion and type checking make development so much easier.
```python
from fastgedcom.base import Document, FakeLine, IndiRef, Record, is_true
from fastgedcom.helpers import format_name

def print_infos(gedcom: Document, indi: IndiRef) -> None:
	record = gedcom[indi]
	if is_true(record): print_name(record)

def print_name(record: Record | FakeLine) -> None:
	print(format_name(record >= "NAME"))

print_infos(document, "@I1@")
```

Iteration on families is fast. Save time!
```python
from fastgedcom.family_aid import FamilyAid

booster = FamilyAid(document)

def number_of_ascendants(indi: Record | FakeLine) -> int:
	if not is_true(indi): return 1
	father, mother = booster.get_parents(indi.tag)
	return 1+max(number_of_ascendants(father), number_of_ascendants(mother))

def number_of_descendants(indi: IndiRef) -> int:
	children = booster.get_children_ref(indi)
	return len(children) + sum(number_of_descendants(c) for c in children)

print(max(number_of_ascendants(indi)
	for indi in document.get_records("INDI")
))
print(max(number_of_descendants(indi.tag)
	for indi in document.get_records("INDI")
))
```

You want to see more? [Here are some examples](https://github.com/GatienBouyer/fastgedcom/tree/main/examples)

I promise you it is efficient! I [test it](https://github.com/GatienBouyer/fastgedcom/tree/main/benchmarks) and I use it.



## Feature details

- Supports reading of gedcom files encoded in UTF-8 with and without BOM, UTF-16 (also named UNICODE), ANSI, and ANSEL.
- ~~Supports export of gedcom files encoded in UTF-8, UTF-16, and ANSI.~~

## Feedbacks

Feedbacks are welcome, and they will be greatly appreciated!

If you like this project, consider putting a star on [Github](https://github.com/GatienBouyer/fastgedcom), thank you!

For any feedback or question, please feel free to contact me by email at gatien.bouyer.dev@gmail.com or via [Github issues](https://github.com/GatienBouyer/fastgedcom/issues).
