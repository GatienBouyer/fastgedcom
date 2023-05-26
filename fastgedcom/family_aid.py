from collections import defaultdict

from .base import (Document, FakeLine, FamRef, IndiRef, Record, TrueLine,
                   fake_line, is_true)


class FamilyAid():
	"""
	The class uses 2 dictionnaries to speed up the process.
	
	The `parents` dictionnary is used to get the parents of someone
	(via the FAMC of the person)
	
	The `unions` dictionnary is used to get the spouses or children
	(via the FAMS of the person)

	Not all methods use those dictionnaries.
	"""

	def __init__(self, document: Document) -> None:
		self.document = document
		self.parents: dict[IndiRef,
		    tuple[Record | FakeLine, Record | FakeLine]]
		self.unions: defaultdict[IndiRef, list[Record]]
		self._build_parents()

	def _build_parents(self) -> None:
		self.parents = dict()
		self.unions = defaultdict(list)
		for fam_record in self.document.level0_index.values():
			if fam_record.payload != "FAM": continue
			children: list[IndiRef] = []
			father: FakeLine | TrueLine = fake_line
			mother: FakeLine | TrueLine = fake_line
			for line in fam_record.sub_lines:
				if line.payload == "": continue
				if line.tag == "CHIL":
					children.append(line.payload)
				elif line.tag == "HUSB":
					father = self.document.level0_index[line.payload]
					self.unions[father.tag].append(fam_record)
				elif line.tag == "WIFE":
					mother = self.document.level0_index[line.payload]
					self.unions[mother.tag].append(fam_record)
			for child in children:
				self.parents[child] = (father, mother)

	def get_parent_family(self, child: TrueLine | FakeLine) -> FamRef | None:
		"""Return the FamRef of the family with the parents of the person."""
		if not is_true(child): return None
		for sub_line in child.sub_lines:
			if sub_line.tag == "FAMC":
				if sub_line.payload == "": return None
				return sub_line.payload
		return None
	
	def get_parents(self,
		child: IndiRef
	) -> tuple[TrueLine | FakeLine, TrueLine | FakeLine]:
		"""Return the father and the mother of the person."""
		return self.parents.get(child, (fake_line, fake_line))

	def get_unions(self, spouse: IndiRef) -> list[FamRef]:
		return [fam.tag for fam in self.unions.get(spouse, [])]

	def get_unions_with(self,
		spouse1: IndiRef,
		spouse2: IndiRef
	) -> list[FamRef]:
		spouse_fams = self.unions.get(spouse1, [])
		return [fam.tag
			for fam in self.unions.get(spouse2, [])
			if fam in spouse_fams]

	def get_children(self, parent: IndiRef) -> list[IndiRef]:
		unions = self.unions.get(parent, [])
		return [sub_line.payload
			for fam in unions for sub_line in fam.sub_lines
			if sub_line.tag == "CHIL" and sub_line.payload != ""]

	def get_children_with(self,
		spouse1: IndiRef,
		spouse2: IndiRef
	) -> list[IndiRef]:
		fams = self.unions.get(spouse1, [])
		unions = [fam for fam in self.unions.get(spouse2, []) if fam in fams]
		return [sub_line.payload
			for fam in unions for sub_line in fam.sub_lines
			if sub_line.tag == "CHIL" and sub_line.payload != ""]

	def get_spouses(self, indi: IndiRef) -> list[IndiRef]:
		return [sub_line.payload
			for fam in self.unions.get(indi, []) for sub_line in fam.sub_lines
			if (sub_line.tag in ("HUSB", "WIFE") and sub_line.payload != indi
				and sub_line.payload != "")]

	def get_siblings(self, indi: IndiRef) -> list[IndiRef]:
		fam_ref = self.get_parent_family(self.document.level0_index[indi])
		if fam_ref is None: return []
		fam_record = self.document.level0_index[fam_ref]
		return [sub_line.payload
			for sub_line in fam_record.sub_lines
			if (sub_line.tag == "CHIL" and sub_line.payload != indi
				and sub_line.payload != "")]

	def get_stepsiblings(self, indi: IndiRef) -> list[IndiRef]:
		parent_family = self.get_parent_family(self.document.level0_index[indi])
		father, mother = self.get_parents(indi)
		unions: list[TrueLine] = []
		if is_true(father):
			unions.extend(self.unions.get(father.tag, []))
		if is_true(mother):
			unions.extend(self.unions.get(mother.tag, []))
		stepsiblings: list[IndiRef] = []
		for fam in unions:
			if fam.tag != parent_family:
				stepsiblings.extend(sub_line.payload
					for sub_line in fam.sub_lines
					if sub_line.tag == "CHIL" and sub_line.payload != "")
		return stepsiblings

	def get_children_per_union(self,
		indi: IndiRef
	) -> list[tuple[IndiRef | None, list[IndiRef]]]:
		"""Return the list of spouse and children for each union
		of the given indi.
		Return different results compared to children_with()
		if the individual marry the same person twice."""
		results: list[tuple[IndiRef | None, list[IndiRef]]] = []
		for fam in self.unions.get(indi, []):
			spouse = None
			children: list[IndiRef] = []
			for sub_line in fam.sub_lines:
				if sub_line.payload == "": continue
				if sub_line.tag == "CHIL":
					children.append(sub_line.payload)
				elif (sub_line.tag in ("HUSB", "WIFE")
					and sub_line.payload != indi):
					spouse = sub_line.payload
			results.append((spouse, children))
		return results
