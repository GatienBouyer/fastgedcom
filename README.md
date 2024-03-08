# FastGedcom

A lightweight tool to parse, browse and edit gedcom files.

Install FastGedcom using pip from [its PyPI page](https://pypi.org/project/fastgedcom/):
```bash
pip install fastgedcom
```
To install the Ansel codecs use the following command. It enables the use of the Ansel text encoding often used for gedcom files.
```bash
pip install fastgedcom[ansel]
```

## Why choosing FastGedcom?

- FastGedcom has less methods, which make it easier to work with.
- FastGedcom has a linear syntax, if blocks are less needed.
- FastGedcom is shorter to write with the use of operator overloading. (optional)
- FastGedcom has a faster parsing.

<table>
	<tr>
		<th>Gedcom file</th>
		<th>FastGedcom</th>
		<th>Other Libraries</th>
	</tr>
	<tr>
		<td><pre><code>
0 HEAD
0 @I1@ INDI
1 NAME John Doe
1 BIRT
2 DATE 1 Jan 1970
1 DEAT
2 DATE 2 Feb 2081
0 TRLR
		</code></pre</td>
		<td><pre><code>
# Faster parsing
document = strict_parse("my-file.ged")
person = document["@I1@"]
# No if chain!
death = person.get_sub_line("DEAT")
date = death.get_sub_line("DATE")
print(date.payload)
# Prints None if the field is missing
		</code></pre></td>
		<td><pre><code>
# With the python-gedcom library
document = Parser("my-file.ged")
person = document.get_element_dictionary()["@I1@"]
death_data = person.get_death_data()
if death_date[1]:
	date = death_date[1]
	if date:
		print(date)
		</code></pre></td>
	</tr>
</table>

## Features

### The least abstraction from gedcom with free choice of formatting
There is a lot of genealogy software out there, and every one of them have its own tags and formats to write information. With the FastGedcom approach, you can easily adapt your code to your gedcom files.

```python
from fastgedcom.parser import strict_parse
from fastgedcom.helpers import extract_name_parts

document = strict_parse("gedcom_file.ged")

name = document["@I1@"] >= "NAME"
print(name) # Unformatted
given_name, surname = extract_name_parts(name)
print(f"{given_name.capitalize()} {surname.upper()}")
```

### Multi-encoding support
It supports gedcom files encoded in UTF-8 (with and without BOM), UTF-16 (also named UNICODE), ANSI, and ANSEL.

### This Option paradigm replaces the if blocks:
If a field is missing, you will get a [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine) containing an empty string. This helps reduce the boilerplate code massively. And, you can differentiate a [TrueLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.TrueLine) from a [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine) with a simple boolean check.
```python

indi = document["@I13@"]

# You can access the date of death, whether the person is deceased or not.
date = (indi > "DEAT") >= "DATE"

# You choose the formatting of the date
print("Death date:", format_date(date))
```

### Typehints for salvation!
Autocompletion and type checking make development so much easier.

- There are only 3 main classes: [Document](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.Document), [TrueLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.TrueLine), and [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine).
- There are type aliases for code clarity: [Record](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.Record), [XRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.XRef), [IndiRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.IndiRef), [FamRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FamRef), and more.

## Why it is called FastGedcom?

FastGedcom's aim is to keep the code close to your gedcom files. So, you don't have to learn what FastGedcom does. The data you have is the data you get. The content of the gedcom file is unchanged and there is no abstraction. Hence, the learning curve of the library is faster than the alternatives. The data processing is optional to best suit your needs. FastGedcom is more of a starting point for your data processing than a feature-rich library.

The name **FastGedcom** doesn't just come from its ease of use. Parsing is the fastest among Python libraries. Especially for parsing and getting the relatives of a person, the [FamilyLink](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/family_link/index.html#fastgedcom.family_link.FamilyLink) class is build for this purpose. Here are the [benchmarks](https://github.com/GatienBouyer/fastgedcom/tree/main/benchmarks).

## Documentation and examples

Want to see more of FastGedcom? Here are some [examples](https://github.com/GatienBouyer/fastgedcom/tree/main/examples)

The [documentation](https://fastgedcom.readthedocs.io/en/latest/) of FastGedcom is available on ReadTheDocs.

## Feedback

Comments and contributions are welcomed, and they will be greatly appreciated!

If you like this project, consider putting a star on [GitHub](https://github.com/GatienBouyer/fastgedcom). Thank you!

For any feedback or questions, please feel free to contact me by email at gatien.bouyer.dev@gmail.com or via [GitHub issues](https://github.com/GatienBouyer/fastgedcom/issues).
