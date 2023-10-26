# FastGedcom

A lightweight tool to parse, browse and edit gedcom files.

Install FastGedcom using pip from [its PyPI page](https://pypi.org/project/fastgedcom/):
```bash
pip install fastgedcom
```

## Features
Easy to write! Free choice of fields, data, and formatting.
```python
from fastgedcom.parser import strict_parse
from fastgedcom.helpers import format_date

document = strict_parse("gedcom_file.ged")

birth_date = (document["@I1@"] > "BIRT") >= "DATE"
print(format_date(birth_date))
```

The syntax is flexible and permissive. If you don't like magic operator overloads, you can use standard methods!

It supports gedcom files encoded in UTF-8 (with and without BOM), UTF-16 (also named UNICODE), ANSI, and ANSEL.

If a field is missing, you will get a [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine) containing an empty string. This helps reduce the boilerplate code massively. And, you can differentiate a [TrueLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.TrueLine) from a [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine) with a simple boolean check.
```python

indi = document["@I13@"]

if not indi > "DEAT":
	print("No DEAT field. The person is alive")

# You can access the date of death, whether the person is deceased or not.
date = (indi > "DEAT") >= "DATE"

# You choose the formatting of the date
print("Death date:", format_date(date))
```

Typehints for salvation! Autocompletion and type checking make development so much easier.

- There are only 3 main classes: [Document](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.Document), [TrueLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.TrueLine), and [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine).
- There are type aliases for code clarity: [Record](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.Record), [XRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.XRef), [IndiRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.IndiRef), [FamRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FamRef), and more.

## Why FastGedcom?

FastGedcom's aim is to keep the code close to your gedcom files. So, you don't have to learn what FastGedcom does, the data you have is the data you get. The content of the gedcom file is unchanged. The data processing is optional to best suit your needs. FastGedcom is more of a starting point for your data processing than a feature-rich library.

The name **FastGedcom** doesn't just come from its ease of use. Parsing is the fastest among Python libraries. And, for getting the relatives of a person as fast as possible, there is the [FamilyLink](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/family_link/index.html#fastgedcom.family_link.FamilyLink) class. Here are the [benchmarks](https://github.com/GatienBouyer/fastgedcom/tree/main/benchmarks).

## Documentation and examples

Want to see more of FastGedcom? Here are some [examples](https://github.com/GatienBouyer/fastgedcom/tree/main/examples)

The [documentation](https://fastgedcom.readthedocs.io/en/latest/) of FastGedcom is available on ReadTheDocs.

## Feedback

Comments are welcome, and they will be greatly appreciated!

If you like this project, consider putting a star on [GitHub](https://github.com/GatienBouyer/fastgedcom). Thank you!

For any feedback or questions, please feel free to contact me by email at gatien.bouyer.dev@gmail.com or via [GitHub issues](https://github.com/GatienBouyer/fastgedcom/issues).
