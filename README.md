# FastGedcom

A lightweight tool to parse, browse and edit gedcom files.

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

If a field is missing, you will get a [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine) containing an empty string. This reduces the boiler plate code. You can differentiate [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine) and [TrueLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.TrueLine) with a simple boolean check.
```python

indi = document["@I13@"]
death = indi > "DEAT"
if not death:
	print("No DEAT field. The person is alive")
# Can continue anyway
print("Death date:", format_date((indi > "DEAT") >= "DATE"))
```

Typehints for salvation! Autocompletion and type checking make development so much easier.

- There are only 3 main classes: [Document](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.Document), [TrueLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.TrueLine), and [FakeLine](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FakeLine).
- There are type aliases for code clarity: [Record](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.Record), [XRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.XRef), [IndiRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.IndiRef), [FamRef](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/base/index.html#fastgedcom.base.FamRef), and more.

## Why FastGedcom ?

FastGedcom's aim is to keep the code close to your gedcom files. So, you don't have to learn what FastGedcom does for you. The content of your gedcom file is what you get. The data processing is optional to best suit your needs.

The name **FastGedcom** doesn't just come from its ease of use. Getting relatives can be done quickly. That's what the [FamilyLink](https://fastgedcom.readthedocs.io/en/latest/autoapi/fastgedcom/family_link/index.html#fastgedcom.family_link.FamilyLink) class is all about. [Here](https://github.com/GatienBouyer/fastgedcom/tree/main/benchmarks) are the benchmark I used.

## Documentation and examples

Want to see more code? [Here are some examples](https://github.com/GatienBouyer/fastgedcom/tree/main/examples)

The documentation of FastGedcom is available [here](https://fastgedcom.readthedocs.io/en/latest/) on ReadTheDocs.

## Feedbacks

Feedbacks are welcome, and they will be greatly appreciated!

If you like this project, consider putting a star on [Github](https://github.com/GatienBouyer/fastgedcom), thank you!

For any feedback or question, please feel free to contact me by email at gatien.bouyer.dev@gmail.com or via [Github issues](https://github.com/GatienBouyer/fastgedcom/issues).
