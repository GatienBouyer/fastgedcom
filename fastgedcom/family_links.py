"""Define the :py:class:`.FamilyLink` class used to bypass family records."""

from collections import defaultdict

from .base import (Document, FakeLine, FamRef, IndiRef, Record, TrueLine,
                   fake_line, is_true)


class FamilyLink():
	"""Class with methods to easily get relatives of someone.

	Methods ending in _ref (such as :py:meth:`.get_parent_family_ref`)
	are called by their non-_ref counterparts (such as
	:py:meth:`.get_parent_family`). Use the first set of methods when
	you need performance. Use the second set of methods for convenience.

	The class uses 2 dictionnaries to speed up the process.
	The `parents` dictionnary is used to get the parents of someone
	(via the FAMC of the person).
	The `unions` dictionnary is used to get the spouses or children
	(via the FAMS of the person).
	Not all methods use those dictionnaries.
	"""

	def __init__(self, document: Document) -> None:
		self.document = document
		self.parents: dict[IndiRef, tuple[Record | FakeLine, Record | FakeLine]]
		self.unions: defaultdict[IndiRef, list[Record]]
		self._build_parents()

	def _build_parents(self) -> None:
		self.parents = dict()
		self.unions = defaultdict(list)
		for fam_record in self.document.records.values():
			if fam_record.payload != "FAM": continue
			children: list[IndiRef] = []
			father: FakeLine | TrueLine = fake_line
			mother: FakeLine | TrueLine = fake_line
			for line in fam_record.sub_lines:
				if line.payload == "@VOID@": continue
				if line.tag == "CHIL":
					children.append(line.payload)
				elif line.tag == "HUSB":
					father = self.document.records[line.payload]
					self.unions[father.tag].append(fam_record)
				elif line.tag == "WIFE":
					mother = self.document.records[line.payload]
					self.unions[mother.tag].append(fam_record)
			for child in children:
				self.parents[child] = (father, mother)

	def get_parent_family_ref(self, child: TrueLine | FakeLine) -> FamRef | None:
		"""Return the family reference with the parents of the person."""
		if not is_true(child): return None
		for sub_line in child.sub_lines:
			if sub_line.tag == "FAMC":
				if sub_line.payload == "@VOID@": return None
				return sub_line.payload
		return None

	def get_parent_family(self, child: TrueLine | FakeLine) -> Record | FakeLine:
		"""Return the family record with the parents of the person."""
		fam_ref = self.get_parent_family_ref(child)
		return self.document.records[fam_ref] if fam_ref else fake_line

	def get_parents(self,
		child: IndiRef
	) -> tuple[Record | FakeLine, Record | FakeLine]:
		"""Return the father and the mother of the person."""
		return self.parents.get(child, (fake_line, fake_line))

	def get_unions(self, spouse: IndiRef) -> list[Record]:
		"""Return the unions of the person."""
		return [fam for fam in self.unions.get(spouse, [])]

	def get_unions_with(self,
		spouse1: IndiRef,
		spouse2: IndiRef
	) -> list[Record]:
		"""Return the unions between the two people."""
		spouse_fams = self.unions.get(spouse1, [])
		return [fam
			for fam in self.unions.get(spouse2, [])
			if fam in spouse_fams]

	def get_children_ref(self, parent: IndiRef) -> list[IndiRef]:
		"""Return the children's references of a person."""
		unions = self.unions.get(parent, [])
		return [sub_line.payload
			for fam in unions for sub_line in fam.sub_lines
			if sub_line.tag == "CHIL" and sub_line.payload != "@VOID@"]

	def get_children(self, parent: IndiRef) -> list[Record]:
		"""Return the children's records of a person."""
		return [self.document.records[child]
			for child in self.get_children_ref(parent)]

	def get_children_with_ref(self,
		spouse1: IndiRef,
		spouse2: IndiRef
	) -> list[IndiRef]:
		"""Return the children's references of the couple."""
		fams = self.unions.get(spouse1, [])
		unions = [fam for fam in self.unions.get(spouse2, []) if fam in fams]
		return [sub_line.payload
			for fam in unions for sub_line in fam.sub_lines
			if sub_line.tag == "CHIL" and sub_line.payload != "@VOID@"]

	def get_children_with(self,
		spouse1: IndiRef,
		spouse2: IndiRef
	) -> list[Record]:
		"""Return the children's records of the couple."""
		return [self.document.records[child]
			for child in self.get_children_with_ref(spouse1, spouse2)]

	def get_spouses_ref(self, indi: IndiRef) -> list[IndiRef]:
		"""Return the spouses' references of the person."""
		return [sub_line.payload
			for fam in self.unions.get(indi, []) for sub_line in fam.sub_lines
			if (sub_line.tag in ("HUSB", "WIFE") and sub_line.payload != indi
				and sub_line.payload != "@VOID@")]

	def get_spouses(self, indi: IndiRef) -> list[Record]:
		"""Return the spouses' records of the person."""
		return [self.document.records[spouse]
			for spouse in self.get_spouses_ref(indi)]

	def get_all_siblings_ref(self, indi: IndiRef) -> list[IndiRef]:
		"""Return the siblings' references of the person.
		Stepsiblings included."""
		father, mother = self.get_parents(indi)
		unions: list[Record] = []
		if is_true(father):
			unions.extend(self.unions.get(father.tag, []))
		if is_true(mother):
			unions.extend(self.unions.get(mother.tag, []))
		return [sub_line.payload
			for fam in unions
			for sub_line in fam.sub_lines
			if (sub_line.tag == "CHIL" and sub_line.payload != "@VOID@"
				and sub_line.payload != indi)]

	def get_all_siblings(self, indi: IndiRef) -> list[Record]:
		"""Return the siblings' records of the person.
		Stepsiblings included."""
		return [self.document.records[sibling]
			for sibling in self.get_all_siblings_ref(indi)]

	def get_siblings_ref(self, indi: IndiRef) -> list[IndiRef]:
		"""Return the siblings' references of the person.
		Stepsiblings excluded."""
		fam = self.get_parent_family(self.document.records[indi])
		return [sub_line.payload
			for sub_line in fam.sub_lines
			if (sub_line.tag == "CHIL" and sub_line.payload != "@VOID@"
				and sub_line.payload != indi)]

	def get_siblings(self, indi: IndiRef) -> list[Record]:
		"""Return the siblings' records of the person.
		Stepsiblings excluded."""
		return [self.document.records[sibling]
			for sibling in self.get_siblings_ref(indi)]

	def get_stepsiblings_ref(self, indi: IndiRef) -> list[IndiRef]:
		"""Return the stepsiblings' references of the person.
		Siblings excluded."""
		parent_fam = self.get_parent_family_ref(self.document.records[indi])
		father, mother = self.get_parents(indi)
		unions: list[Record] = []
		if is_true(father):
			unions.extend(self.unions.get(father.tag, []))
		if is_true(mother):
			unions.extend(self.unions.get(mother.tag, []))
		stepsiblings: list[IndiRef] = []
		for fam in unions:
			if fam.tag != parent_fam:
				stepsiblings.extend(sub_line.payload
					for sub_line in fam.sub_lines
					if sub_line.tag == "CHIL" and sub_line.payload != "@VOID@")
		return stepsiblings

	def get_stepsiblings(self, indi: IndiRef) -> list[Record]:
		"""Return the stepsiblings of the person.
		Siblings excluded."""
		return [self.document.records[stepsibling]
			for stepsibling in self.get_stepsiblings_ref(indi)]

	def get_spouse_in_fam_ref(self, indi: IndiRef, fam: Record) -> IndiRef:
		"""Return the spouse's reference of the family that is not the person's."""
		husban = fam >= "HUSB"
		wife = fam >= "WIFE"
		if wife == indi: return husban
		return wife

	def get_spouse_in_fam(self, indi: IndiRef, fam: Record) -> Record:
		"""Return the spouse's record of the family that is not the person's."""
		return self.document.records[self.get_spouse_in_fam_ref(indi, fam)]
