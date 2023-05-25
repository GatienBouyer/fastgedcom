from typing import Iterator, Literal, TypeAlias, TypeGuard, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

SubmRef: TypeAlias = str
"""The cross-reference identifier of type '@SUB1@' or '@U1@' for a submitter of the document."""
SubnRef: TypeAlias = str
"""Deprecated. The cross-reference identifier of type '@SUB1@' for a submission."""
IndiRef: TypeAlias = str
"""The cross-reference identifier of type '@I1@' for an individual."""
FamRef: TypeAlias = str
"""The cross-reference identifier of type '@F1@' for a family."""
SNoteRef: TypeAlias = str
"""The cross-reference identifier of type '@N1@' for a shared note."""
SourRef: TypeAlias = str
"""The cross-reference identifier of type '@S1@' for a source document."""
RepoRef: TypeAlias = str
"""The cross-reference identifier of type '@R1@' for a repository (an archive)."""
ObjeRef: TypeAlias = str
"""The cross-reference identifier of type '@O1@' for an object (e.g. an image)."""

XRef: TypeAlias = SubmRef | SubnRef | IndiRef | FamRef | SNoteRef | SourRef | RepoRef | ObjeRef
"""The cross-reference identifier indicates a record to which payloads may point. """

VoidRef: TypeAlias = Literal['@VOID@']
"""A pointer used for unknown value and to have something in the payload.
e.g.: in a family record, the line '2 CHIL @VOID@' indicates that the parents had a child whom we know nothing."""

Pointer: TypeAlias = XRef | VoidRef
"""Generic pointer that is used in the payload to reference an existing record or a non-existing one."""

class Line(ABC):
	"""Abstract base class for gedcom lines.
	(see GedcomLine for more information)
	This class is for syntactic sugar. It defines operator
	as alias of standard methods and allows the chaining of
	operations thanks to the FakeLine implementation.
	
	Example:
	```python
	# With standard methods:
	indi = gedcom.get_record("@I1@")
	birth_date = indi.get_sub_record("BIRT").get_sub_record_value("DATE")
	sources = indi.get_sub_record("BIRT").get_sub_records("SOUR").
	
	# With magic methods:
	indi = gedcom["@I1@"]
	birth_date = indi > "BIRT" >= "DATE"
	sources = indi > "BIRT" >> "SOUR"
	```
	"""
	@property
	@abstractmethod
	def payload(self) -> str: ...
	
	@property
	@abstractmethod
	def payload_with_cont(self) -> str: ...

	@abstractmethod
	def get_sub_records(self, tag: str) -> list['GedcomLine']: ...
	
	@abstractmethod
	def get_sub_record(self, tag: str) -> Union['GedcomLine', 'FakeLine']: ...
	
	@abstractmethod
	def get_sub_record_payload(self, tag: str) -> str: ...

	__gt__ = get_sub_record # operator >
	__ge__ = get_sub_record_payload # operator >=
	__rshift__ = get_sub_records # operator >>

class FakeLine(Line):
	"""Dummy Line that allows the chaining of operators.

	To differenciate a FakeLine from a GedcomLine a simple boolean test is
	enough: `if line: line.payload`. However to tell typecheckers that after
	the test it the type is narrowed, you should use the line_exists
	function.

	In general, the use of `get_sub_record_payload` (or `>=`) is preferable.

	Example:
	```python
	# Instead of:
	indi_birth_date = (gedcom.get_record("@I1@") > "BIRT") > "DATE"
	if line_exists(indi_birth_date):
		print(indi_birth_date.payload)

	# Prefere the use of:
	indi_birth_date = (gedcom.get_record("@I1@") > "BIRT") >= "DATE"
	print(indi_birth_date)
	```
	"""
	payload = ""
	payload_with_cont = ""
	
	def get_sub_records(self, tag: str) -> list['GedcomLine']:
		return []
	
	def get_sub_record(self, tag: str) -> Union['GedcomLine', 'FakeLine']:
		return fake_line
	
	def get_sub_record_payload(self, tag: str) -> str:
		return ""
	
	__gt__ = get_sub_record # operator >
	__ge__ = get_sub_record_payload # operator >=
	__rshift__ = get_sub_records # operator >>
	
	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__}>"
	
	def __bool__(self) -> bool:
		return False


@dataclass(slots=True)
class GedcomLine(Line):
	"""Represent a line of a gedcom document and contains the sub-lines
	to traverse the gedcom tree structure.

	This class use the simplified 'Level Tag Payload' structure,
	instead of the normalized 'Level [Xref] Tag [LineVal]' gedcom structure.
	In this structure, the Tag is either the normalized Tag or the optional Xref.
	Hence, the Payload is the LineVal when the Xref is not present,
	or the Payload is the normalized Tag plus the LineVal when the Xref is present.
	When the line contains neither a Xref or a LineVal, the Payload is an empty string.
	"""
	level: int
	tag: str | XRef
	payload: str
	sub_rec: list['GedcomLine'] = field(default_factory=list)

	def get_sub_records(self, tag: str) -> list['GedcomLine']:
		return [sub_record for sub_record in self.sub_rec if sub_record.tag == tag]

	def get_sub_record(self, tag: str) -> Union['GedcomLine', 'FakeLine']:
		for sub_record in self.sub_rec:
			if sub_record.tag == tag:
				return sub_record
		return fake_line

	def get_sub_record_payload(self, tag: str) -> str:
		for sub_record in self.sub_rec:
			if sub_record.tag == tag:
				return sub_record.payload
		return ""
	
	__gt__ = get_sub_record # operator >
	__ge__ = get_sub_record_payload # operator >=
	__rshift__ = get_sub_records # operator >>

	def __str__(self) -> str:
		return f"{self.level} {self.tag} {self.payload}"

	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__} {self.level} {self.tag} {self.payload} -> {len(self.sub_rec)}>"

	@property
	def payload_with_cont(self) -> str:
		"""The ilne payload with the payload of the CONT sub-records."""
		text = self.payload
		for cont in self.get_sub_records('CONT'):
			text += '\n' + cont.payload
		return text


class Gedcom():
	"""Stores all the information of the gedcom document.
	
	All level 0 records are directly accessible and the higher level records
	are accessible via GedcomLine.sub_rec of the parent record.
	
	Example:
	```python
	gedcom = Gedcom()

	# Iterate over all records
	for rec in gedcom: print(rec.tag)

	# Iterate over individuals:
	for rec in gedcom.get_records("INDI"): print(rec.tag)

	# Get the record by XRef using standard method:
	indi = gedcom.get_record("@I1@")

	# Get the record by XRef using magic method:
	indi = gedcom["@I1@"]
	```	
	"""

	def __init__(self) -> None:
		self.level0_index: dict[XRef, GedcomLine] = dict() #to get records

	def __iter__(self) -> Iterator[GedcomLine]:
		return iter(self.level0_index.values())

	def get_records(self, record_type: str) -> Iterator[GedcomLine]:
		for record in self.level0_index.values():
			if record.payload == record_type:
				yield record

	def get_record(self, identifier: XRef) -> GedcomLine | FakeLine:
		return self.level0_index.get(identifier, fake_line)
	__getitem__ = get_record

fake_line = FakeLine()

def line_exists(line: Union[GedcomLine, FakeLine]) -> TypeGuard[GedcomLine]:
	return bool(line)
