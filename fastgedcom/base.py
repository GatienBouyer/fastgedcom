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
	"""
	Abstract base class for gedcom lines i.e. TrueLine and FakeLine.
	See TrueLine and FakeLine for more information.
	"""
	@property
	@abstractmethod
	def payload(self) -> str: ...
	
	@property
	@abstractmethod
	def payload_with_cont(self) -> str: ...

	@abstractmethod
	def get_sub_lines(self, tag: str) -> list['TrueLine']: ...
	
	@abstractmethod
	def get_sub_line(self, tag: str) -> Union['TrueLine', 'FakeLine']: ...
	
	@abstractmethod
	def get_sub_line_payload(self, tag: str) -> str: ...

	__gt__ = get_sub_line # operator >
	__ge__ = get_sub_line_payload # operator >=
	__rshift__ = get_sub_lines # operator >>

class FakeLine(Line):
	"""
	Dummy Line for syntactic sugar.
	It allows the chaining of operators.
	
	Example:
	```python
	# With standard methods:
	indi = document.get_line("@I1@")
	birth_date = indi.get_sub_line("BIRT").get_sub_line_payload("DATE")
	sources = indi.get_sub_line("BIRT").get_sub_lines("SOUR").
	
	# With magic methods:
	indi = document["@I1@"]
	birth_date = indi > "BIRT" >= "DATE"
	sources = indi > "BIRT" >> "SOUR"
	```


	To differenciate a FakeLine from a TrueLine a simple boolean test is
	enough: `if line: line.payload`. However to tell typecheckers that after
	the test it the type is narrowed, you should use the is_true
	function.

	In general, the use of `get_sub_line_payload` (or `>=`) is preferable.

	Example:
	```python
	# Instead of:
	indi_birth_date = (document.get_line("@I1@") > "BIRT") > "DATE"
	if line_exists(indi_birth_date):
		print(indi_birth_date.payload)

	# Prefere the use of:
	indi_birth_date = (document.get_line("@I1@") > "BIRT") >= "DATE"
	print(indi_birth_date)
	```
	"""
	payload = ""
	payload_with_cont = ""
	
	def get_sub_lines(self, tag: str) -> list['TrueLine']:
		return []
	
	def get_sub_line(self, tag: str) -> Union['TrueLine', 'FakeLine']:
		return fake_line
	
	def get_sub_line_payload(self, tag: str) -> str:
		return ""
	
	__gt__ = get_sub_line # operator >
	__ge__ = get_sub_line_payload # operator >=
	__rshift__ = get_sub_lines # operator >>
	
	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__}>"
	
	def __bool__(self) -> bool:
		return False


@dataclass(slots=True)
class TrueLine(Line):
	"""
	Represent a line of a gedcom document and contains the sub-lines
	to traverse the gedcom tree structure.

	This class use the simplified 'Level Tag Payload' structure, instead of
	the normalized 'Level [Xref] Tag [LineVal]' gedcom structure. In this
	structure, the Tag is either the normalized Tag or the optional Xref.
	Hence, the Payload is the LineVal when the Xref is not present, or the
	Payload is the normalized Tag plus the LineVal when the Xref is present.
	When the line contains neither a Xref or a LineVal, the Payload is an
	empty string.
	"""
	level: int
	tag: str | XRef
	payload: str
	sub_lines: list['TrueLine'] = field(default_factory=list)

	def get_sub_lines(self, tag: str) -> list['TrueLine']:
		return [sub_line for sub_line in self.sub_lines if sub_line.tag == tag]

	def get_sub_line(self, tag: str) -> Union['TrueLine', 'FakeLine']:
		for sub_line in self.sub_lines:
			if sub_line.tag == tag:
				return sub_line
		return fake_line

	def get_sub_line_payload(self, tag: str) -> str:
		for sub_line in self.sub_lines:
			if sub_line.tag == tag:
				return sub_line.payload
		return ""
	
	__gt__ = get_sub_line # operator >
	__ge__ = get_sub_line_payload # operator >=
	__rshift__ = get_sub_lines # operator >>

	def __str__(self) -> str:
		return f"{self.level} {self.tag} {self.payload}"

	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__} {self.level} {self.tag} {self.payload} -> {len(self.sub_lines)}>"

	@property
	def payload_with_cont(self) -> str:
		"""The line payload with the payload of the CONT sub-lines."""
		text = self.payload
		for cont in self.get_sub_lines('CONT'):
			text += '\n' + cont.payload
		return text


Record: TypeAlias = TrueLine
"""A level 0 line referenced by an XRef in the document."""

class Document():
	"""
	Stores all the information of the gedcom document.
	
	All records (level 0 lines) are directly accessible via dict and the
	other level lines are accessible via TrueLine.sub_lines of the parent line.
	
	Example:
	```python
	document = Document()

	# Iterate over all records
	for rec in document: print(rec.tag)

	# Iterate over individuals:
	for rec in document.get_records("INDI"): print(rec.tag)

	# Get the record by XRef using standard method:
	indi = document.get_record("@I1@")

	# Get the record by XRef using magic method:
	indi = document["@I1@"]
	```	
	"""

	def __init__(self) -> None:
		self.level0_index: dict[XRef, Record] = dict()

	def __iter__(self) -> Iterator[Record]:
		return iter(self.level0_index.values())

	def get_records(self, record_type: str) -> Iterator[Record]:
		for record in self.level0_index.values():
			if record.payload == record_type:
				yield record

	def get_record(self, identifier: XRef | Literal["HEAD"]) -> Record | FakeLine:
		return self.level0_index.get(identifier, fake_line)
	__getitem__ = get_record

fake_line = FakeLine()

def is_true(line: Union[TrueLine, FakeLine]) -> TypeGuard[TrueLine]:
	return bool(line)
