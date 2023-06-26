"""Classes and types for the data structure used to represent a gedcom."""

from typing import Iterator, Literal, TypeAlias
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

SubmRef: TypeAlias = str
"""The cross-reference identifier of type '@SUB1@' or '@U1@' for a submitter
of the document."""
SubnRef: TypeAlias = str
"""Deprecated. The cross-reference identifier of type '@SUB2@' for a submission."""
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
"""The cross-reference identifier indicates a record to which payloads may point."""

VoidRef: TypeAlias = Literal['@VOID@']
"""A pointer used for unknown value where payload can't be let empty.

e.g.: In a family record, the line '2 CHIL @VOID@' indicates that the parents
had a child whom we know nothing. The line is used to keep the children birth order."""

Pointer: TypeAlias = XRef | VoidRef
"""Generic pointer that is used in the payload to reference an existing record
or a non-existing one."""


class Line(ABC):
	"""Abstract base class for gedcom lines.

	Implementations are :py:class:`.TrueLine` and :py:class:`.FakeLine`,
	see these classes for more information.
	"""
	@abstractmethod
	def __bool__(self) -> bool:
		"""True if it is a :py:class:`.TrueLine`,
		False if it is a :py:class:`.FakeLine`."""

	@property
	@abstractmethod
	def payload(self) -> str:
		"""See the description of :py:class:`.TrueLine` class."""

	@property
	@abstractmethod
	def payload_with_cont(self) -> str:
		"""The content of this gedcom field, namely the payload combined
		with all CONT and CONC sub-lines."""

	@abstractmethod
	def get_sub_lines(self, tag: str) -> list['TrueLine']:
		"""Return the all sub-lines having the given :any:`tag`.
		An empty list if no line matches."""

	def __rshift__(self, tag: str) -> list['TrueLine']:
		"""Alias for :py:meth:`get_sub_lines` to shorten the syntax
		by using the >> operator."""
		return self.get_sub_lines(tag)

	@abstractmethod
	def get_sub_line(self, tag: str) -> 'TrueLine | FakeLine':
		"""Return the first sub-line having the given :any:`tag`.
		A :py:class:`.FakeLine` if no line matches."""

	def __gt__(self, tag: str) -> 'TrueLine | FakeLine':
		"""Alias for :py:meth:`get_sub_line` to shorten the syntax
		by using the > operator."""
		return self.get_sub_line(tag)

	@abstractmethod
	def get_sub_line_payload(self, tag: str) -> str:
		"""Return the payload of the first sub-line having the given
		:any:`tag`. An empty string if no line matches."""

	def __ge__(self, tag: str) -> str:
		"""Alias for :py:meth:`get_sub_line_payload` to shorten the syntax
		by using the >= operator."""
		return self.get_sub_line_payload(tag)


class FakeLine(Line):
	"""Dummy line for syntactic sugar.

	It allows the chaining of method calls. See these `examples
	<https://github.com/GatienBouyer/fastgedcom/tree/main/examples>`_
	for the usage of chaining.

	The class behave like a :py:class:`.TrueLine`
	(It has the same methods), but the payload is empty.

	To differentiate a :py:class:`.FakeLine` from a
	:py:class:`.TrueLine` a simple boolean test is enough.
	"""

	payload = "" # pyright: ignore[reportGeneralTypeIssues]
	payload_with_cont = "" # pyright: ignore[reportGeneralTypeIssues]
	sub_lines: list['TrueLine'] = []

	def __bool__(self) -> Literal[False]:
		"""Return False."""
		return False

	def get_sub_lines(self, tag: str) -> list['TrueLine']:
		return []

	def __rshift__(self, tag: str) -> list['TrueLine']:
		return self.get_sub_lines(tag)

	def get_sub_line(self, tag: str) -> 'TrueLine | FakeLine':
		return fake_line

	def __gt__(self, tag: str) -> 'TrueLine | FakeLine':
		return self.get_sub_line(tag)

	def get_sub_line_payload(self, tag: str) -> str:
		return ""

	def __ge__(self, tag: str) -> str:
		return self.get_sub_line_payload(tag)

	def __repr__(self) -> str:
		"""Return the string representation of the class."""
		return f"<{self.__class__.__qualname__}>"

	def __eq__(self, value: object) -> bool:
		return isinstance(value, FakeLine)


@dataclass(slots=True)
class TrueLine(Line):
	"""Represent a line of a gedcom document.

	Contain the :py:attr:`sub-lines` of the gedcom structure.

	This class uses the simplified ``Level Tag Payload`` format, instead of
	the normalized ``Level [Xref] Tag [LineVal]`` format. In the simplified
	format, the :py:attr:`tag` is either the normalized Tag or the optional
	Xref. Hence, the :py:attr:`payload` is the LineVal - when the Xref is not
	present - or the normalized Tag plus the LineVal (generally an empty
	string) - when the Xref is present. The Payload can be an empty string. As
	for the :py:attr:`level`, it matches the definition of the gedcom standard.
	"""

	level: int
	"""The line level defined by the gedcom standard."""

	tag: str | XRef
	"""The cross-reference identified if it is a :py:const:`Record`,
	or the tag - as defined in the gedcom standard - defining the structure
	type."""

	payload: str
	"""The payload of the structure, also called content or value.
	Warning: Multi-line payloads are split into several lines according to the
	gedcom standard. Use the :py:attr:`payload_with_cont` property to get the
	complete multi-line payloads."""

	sub_lines: list['TrueLine'] = field(default_factory=list)
	"""List of the sub-lines, i.e. the next-level lines that are part
	of this structure."""

	def __bool__(self) -> Literal[True]:
		"""Return True."""
		return True

	def get_sub_lines(self, tag: str) -> list['TrueLine']:
		return [sub_line for sub_line in self.sub_lines if sub_line.tag == tag]

	def __rshift__(self, tag: str) -> list['TrueLine']:
		return self.get_sub_lines(tag)

	def get_sub_line(self, tag: str) -> 'TrueLine | FakeLine':
		for sub_line in self.sub_lines:
			if sub_line.tag == tag:
				return sub_line
		return fake_line

	def __gt__(self, tag: str) -> 'TrueLine | FakeLine':
		return self.get_sub_line(tag)

	def get_sub_line_payload(self, tag: str) -> str:
		for sub_line in self.sub_lines:
			if sub_line.tag == tag:
				return sub_line.payload
		return ""

	def __ge__(self, tag: str) -> str:
		return self.get_sub_line_payload(tag)

	def __str__(self) -> str:
		"""Return the gedcom representation of the line (sub-lines excluded)."""
		if not self.payload: return f"{self.level} {self.tag}"
		return f"{self.level} {self.tag} {self.payload}"

	def __repr__(self) -> str:
		"""Return the string representation of the class."""
		return f"<{self.__class__.__qualname__} {self.level} {self.tag} {self.payload} -> {len(self.sub_lines)}>"

	@property
	def payload_with_cont(self) -> str:
		text = self.payload
		for sub_line in self.sub_lines:
			if sub_line.tag == "CONT":
				text += '\n' + sub_line.payload
			elif sub_line.tag == "CONC":
				text += sub_line.payload
		return text


Record: TypeAlias = TrueLine
"""A level 0 line referenced by an XRef in the document."""


class Document():
	"""Store all the information of the gedcom document.

	All records (level 0 lines) are directly accessible via the
	:py:attr:`records` dictionnary and the other lines level are
	accessible via :py:attr:`.TrueLine.sub_lines`."""

	records: dict[XRef, Record]
	"""Dictionnary of records, accessible via :py:meth:`get_records` or
	:py:meth:`__getitem__`. Access it directly to raise KeyError instead
	of getting a :py:class:`.FakeLine`. Usefull when you a pretty sure of
	the Record existing in the document."""

	def __init__(self) -> None:
		self.records = dict()

	def __iter__(self) -> Iterator[Record]:
		"""Iterate on the lines of level 0
		(the records, the header, and the TRLR line)."""
		return iter(self.records.values())

	def __contains__(self, identifier: XRef) -> bool:
		"""Return True if the identifier refers to an existing record."""
		return identifier in self.records

	def get_records(self, record_type: str) -> Iterator[Record]:
		"""Return an iterator over records of that ``record_type``
		(i.e. the :py:attr:`~.TrueLine.payload` of level 0 lines)."""
		for record in self.records.values():
			if record.payload == record_type:
				yield record

	__rshift__ = get_records
	"""Alias for :py:meth:`get_records` to shorten the syntax
	by using the >> operator."""

	def get_record(self, identifier: XRef | Literal["HEAD"]) -> Record | FakeLine:
		"""Return the record under that ``identifier``."""
		return self.records.get(identifier, fake_line)

	__getitem__ = get_record
	"""Alias for :py:meth:`get_record` to shorten the syntax
	by using the [] operator."""

	def __eq__(self, __value: object) -> bool:
		if not isinstance(__value, Document):
			return False
		return self.records == __value.records


fake_line = FakeLine()
""":py:class:`.FakeLine` instance returned by functions.
Used to avoid having multiple unnecessary instances of :py:class:`.FakeLine`."""
