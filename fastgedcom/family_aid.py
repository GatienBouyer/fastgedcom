from .base import FakeLine, FamRef, Gedcom, GedcomLine, IndiRef


class FamilyAid():
	def __init__(self, gedcom: Gedcom) -> None:
		self.gedcom = gedcom
		self.parents: dict[IndiRef, tuple[IndiRef | None, IndiRef | None]] = dict() # to get parents
		self.unions: dict[IndiRef, list[FamRef]] = dict() # to get children and spouses
		self._build_parents()
	
	def _build_parents(self) -> None:
		for fam_record in self.gedcom.level0_index.values():
			if fam_record.payload != "FAM": continue
			father = mother = None
			children = []
			for record in fam_record.sub_rec:
				if record.payload is None: continue
				if record.tag == "CHIL":
					children.append(record.payload)
				elif record.tag == "HUSB":
					father = record.payload
					if father in self.unions:
						self.unions[father].append(fam_record.tag)
					else: self.unions[father] = [fam_record.tag]
				elif record.tag == "WIFE":
					mother = record.payload
					if mother in self.unions:
						self.unions[mother].append(fam_record.tag)
					else: self.unions[mother] = [fam_record.tag]
			for child in children:
				self.parents[child] = (father, mother)


	def get_parent_family(self, child: IndiRef) -> FamRef | None:
		"""Return the FamRef of the family with the parents of the person."""
		record = self.gedcom.level0_index.get(child, None)
		if record is None: return None
		for sub_record in record.sub_rec:
			if sub_record.tag == "FAMC":
				if sub_record.payload == "": return None
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
			record = self.gedcom.level0_index[fam]
			for sub_record in record.sub_rec:
				if sub_record.tag == "CHIL":
					if sub_record.payload == "": continue
					children.append(sub_record.payload)
		return children

	def get_unions(self,
		parent: IndiRef,
		spouse: IndiRef | None = None
	) -> list[FamRef]:
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
			record = self.gedcom.level0_index[fam]
			for sub_record in record.sub_rec:
				if sub_record.payload != indi and (sub_record.tag == "HUSB" or sub_record.tag == "WIFE"):
					if sub_record.payload == "": continue
					spouses.append(sub_record.payload)
		return spouses

	def get_siblings(self, indi: IndiRef) -> list[IndiRef]:
		fam = self.get_parent_family(indi)
		if fam is None: return []
		record = self.gedcom.level0_index[fam]
		siblings: list[IndiRef] = []
		for sub_record in record.sub_rec:
			if sub_record.payload != indi and sub_record.tag == "CHIL":
				if sub_record.payload == "": continue
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
			record = self.gedcom.level0_index[fam]
			spouse = None
			children: list[IndiRef] = []
			for sub_record in record.sub_rec:
				if sub_record.tag == "CHIL":
					if sub_record.payload == "": continue
					children.append(sub_record.payload)
				elif sub_record.payload != indi and (sub_record.tag == "HUSB" or sub_record.tag == "WIFE"):
					if sub_record.payload == "": continue
					spouse = sub_record.payload
			unions.append((spouse, children))
		return unions


