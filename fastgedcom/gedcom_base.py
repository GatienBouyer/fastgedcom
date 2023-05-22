from typing import Iterable, Iterator
from dataclasses import dataclass

from .gedcom_structure import FamRef, IndiRef, XRef


@dataclass(slots=True)
class GedcomLine():
	"""Represent a line of a gedcom document and contains the sub-lines
	to traverse the gedcom tree structure.

	This class use the simplified 'Level Tag Payload EOL' structure
	(instead of the normalized 'Level [Xref] Tag [LineVal] EOL' structure).
	In this structure, the Tag is either the normalized Tag or the optional Xref.
	Hence, the Payload is the LineVal when the Xref is not present,
	or the Payload is the normalized Tag plus the LineVal when the Xref is present.
	When the line contains neither a Xref or a LineVal, the Payload is None."""
	level: int
	tag: str | XRef
	payload: str | None
	sub_rec: list['GedcomLine']

	def __str__(self) -> str:
		return f"{self.level} {self.tag} {self.payload if self.payload else ''}"

	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__}{self.level} {self.tag} {self.payload} -> {len(self.sub_rec)}>"

	def all_sub_rec_recursive(self) -> Iterable['GedcomLine']:
		sub_records = list(self.sub_rec)
		while len(sub_records) > 0:
			record = sub_records.pop(0)
			yield record
			sub_records = record.sub_rec + sub_records

	def get_sub_records(self, tag: str) -> list['GedcomLine']:
		return [sub_record for sub_record in self.sub_rec if sub_record.tag == tag]

	def get_sub_record_payload(self, tag: str) -> str | None:
		for sub_record in self.sub_rec:
			if sub_record.tag == tag:
				return sub_record.payload
		return None

	def get_sub_record(self, tag: str) -> 'GedcomLine | None':
		for sub_record in self.sub_rec:
			if sub_record.tag == tag:
				return sub_record
		return None

class Gedcom():
	"""Stores all the information of the gedcom document.
	
	All level 0 records are directly accessible and the higher level records
	are accessible via GedcomLine.sub_rec of the parent record."""

	def __init__(self) -> None:
		self.level0_index: dict[XRef, GedcomLine] = dict() #to get records
		self.parents: dict[IndiRef, tuple[IndiRef | None, IndiRef | None]] = dict() # to get parents
		self.unions: dict[IndiRef, list[FamRef]] = dict() # to get children and spouses

	def __iter__(self) -> Iterator[GedcomLine]:
		return iter(self.level0_index.values())

	def get_records(self, record_type: str) -> Iterator[GedcomLine]:
		for record in self.level0_index.values():
			if record.payload == record_type:
				yield record

	def get_record(self, identifier: XRef) -> GedcomLine | None:
		return self.level0_index.get(identifier, None)

	def get_parent_family(self, child: IndiRef) -> FamRef | None:
		"""Return the FamRef of the family with the parents of the person."""
		record = self.level0_index.get(child, None)
		if record is None: return None
		for sub_record in record.sub_rec:
			if sub_record.tag == "FAMC":
				return sub_record.payload
		return None

	def get_parents(self, child: IndiRef) -> tuple[IndiRef | None, IndiRef | None]:
		"""Return the IndiRef of the father and the IndiRef of the mother of the person.
		Parameter is the IndiRef of the child.
		Return the tuple (father, mother) with None in case of missing data."""
		return self.parents.get(child, (None, None))

	def get_children(self, parent: IndiRef, spouse: IndiRef | None = None) -> list[IndiRef]:
		children: list[IndiRef] = []
		unions: list[FamRef]
		if spouse is None: unions = self.unions.get(parent, [])
		else: unions = self.get_unions(parent, spouse)
		for fam in unions:
			record = self.level0_index[fam]
			for sub_record in record.sub_rec:
				if sub_record.tag == "CHIL":
					if sub_record.payload is None: continue
					children.append(sub_record.payload)
		return children

	def get_unions(self, parent: IndiRef, spouse: IndiRef | None = None) -> list[FamRef]:
		if spouse is None:
			return self.unions.get(parent, [])
		unions: list[FamRef] = []
		spouse_fams = self.unions.get(spouse, [])
		for fam in self.unions.get(parent, []):
			if fam in spouse_fams:
				unions.append(fam)
		return unions

	def get_spouses(self, indi: IndiRef) -> list[IndiRef]:
		spouses: list[IndiRef] = []
		for fam in self.unions.get(indi, []):
			record = self.level0_index[fam]
			for sub_record in record.sub_rec:
				if sub_record.payload != indi and (sub_record.tag == "HUSB" or sub_record.tag == "WIFE"):
					if sub_record.payload is None: continue
					spouses.append(sub_record.payload)
		return spouses

	def get_siblings(self, indi: IndiRef) -> list[IndiRef]:
		fam = self.get_parent_family(indi)
		if fam is None: return []
		record = self.level0_index[fam]
		siblings: list[IndiRef] = []
		for sub_record in record.sub_rec:
			if sub_record.payload != indi and sub_record.tag == "CHIL":
				if sub_record.payload is None: continue
				siblings.append(sub_record.payload)
		return siblings

	def get_stepsiblings(self, indi: IndiRef) -> list[IndiRef]:
		father, mother = self.get_parents(indi)
		stepsiblings: set[IndiRef] = set()
		if father: stepsiblings.update(self.get_children(father))
		if mother: stepsiblings.update(self.get_children(mother))
		if indi in stepsiblings: stepsiblings.remove(indi)
		for child in self.get_siblings(indi):
			stepsiblings.remove(child)
		return list(stepsiblings)

	def get_spouse_children_per_union(self, indi: IndiRef) -> list[tuple[IndiRef | None, list[IndiRef]]]:
		unions: list[tuple[IndiRef | None, list[IndiRef]]] = []
		for fam in self.unions.get(indi, []):
			record = self.level0_index[fam]
			spouse = None
			children: list[IndiRef] = []
			for sub_record in record.sub_rec:
				if sub_record.tag == "CHIL":
					if sub_record.payload is None: continue
					children.append(sub_record.payload)
				elif sub_record.payload != indi and (sub_record.tag == "HUSB" or sub_record.tag == "WIFE"):
					spouse = sub_record.payload
			unions.append((spouse, children))
		return unions
