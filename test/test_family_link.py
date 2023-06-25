import unittest
from pathlib import Path

from fastgedcom.base import Document, fake_line
from fastgedcom.family_link import FamilyLink
from fastgedcom.parser import strict_parse

gedcom_file = Path(__file__).parent / "test_data" / "relatives.ged"

class TestFamilyLink(unittest.TestCase):
	document: Document
	linker: FamilyLink

	@classmethod
	def setUpClass(cls) -> None:
		cls.document = strict_parse(gedcom_file)
		cls.linker = FamilyLink(cls.document)

	def test_get_parent_family(self) -> None:
		self.assertEqual(
			self.linker.get_parent_family(self.document.records["@I1@"]),
			self.document.records["@F1@"]
		)
		self.assertEqual(
			self.linker.get_parent_family(self.document.records["@I21@"]),
			fake_line
		)

	def test_get_parents(self) -> None:
		self.assertEqual(
			self.linker.get_parents("@I1@"),
			(self.document.records["@I2@"], self.document.records["@I3@"])
		)
		self.assertEqual(
			self.linker.get_parents("@I2@"),
			(self.document.records["@I19@"], fake_line)
		)
		self.assertEqual(
			self.linker.get_parents("@I21@"),
			(fake_line, fake_line)
		)

	def test_get_unions(self) -> None:
		self.assertCountEqual(
			self.linker.get_unions("@I1@"),
			[self.document.records["@F2@"], self.document.records["@F3@"]]
		)

	def test_get_unions_with(self) -> None:
		self.assertCountEqual(
			self.linker.get_unions_with("@I1@", "@I4@"),
			[self.document.records["@F2@"]]
		)

	def test_get_spouses(self) -> None:
		self.assertCountEqual(self.linker.get_spouses_ref("@I1@"), ["@I4@", "@I5@"])

	def test_get_spouse_in_fam(self) -> None:
		self.assertEqual(
			self.linker.get_spouse_in_fam_ref("@I1@", self.document.records["@F2@"]),
			"@I4@"
		)
		self.assertEqual(
			self.linker.get_spouse_in_fam_ref("@I1@", self.document.records["@F10@"]),
			None
		)
		self.assertEqual(
			self.linker.get_spouse_in_fam_ref("@I6@", self.document.records["@F4@"]),
			None
		)

	def test_get_children(self) -> None:
		self.assertCountEqual(self.linker.get_children_ref("@I1@"), ["@I6@", "@I7@", "@I41@"])

	def test_get_children_with(self) -> None:
		self.assertCountEqual(self.linker.get_children_with_ref("@I1@", "@I5@"), ["@I7@", "@I41@"])

	def test_siblings(self) -> None:
		self.assertCountEqual(self.linker.get_siblings_ref("@I7@"), ["@I41@"])
		self.assertCountEqual(self.linker.get_stepsiblings_ref("@I7@"), ["@I6@"])
		self.assertCountEqual(self.linker.get_all_siblings_ref("@I7@"), ["@I6@", "@I41@"])

	def test_get_relatives(self) -> None:
		person_id = "@I1@"
		parents = self.linker.get_relatives_ref(person_id, 1)
		grandparents = self.linker.get_relatives_ref(person_id, 2)
		grandchildren = self.linker.get_relatives_ref(person_id, -2)
		siblings = self.linker.get_relatives_ref(person_id, 0, 1)
		cousins = self.linker.get_relatives_ref(person_id, 0, 2)
		second_cousins = self.linker.get_relatives_ref(person_id, 0, 3)
		oncles_and_aunts = self.linker.get_relatives_ref(person_id, 1, 1)
		siblings_of_grandparents = self.linker.get_relatives_ref(person_id, 2, 1)
		cousins_of_parents = self.linker.get_relatives_ref(person_id, 1, 2)
		nephews_and_nieces = self.linker.get_relatives_ref(person_id, -1, 1)
		grandchildren_of_siblings = self.linker.get_relatives_ref(person_id, -2, 1)
		children_of_cousins = self.linker.get_relatives_ref(person_id, -1, 2)
		self.assertCountEqual(parents, ["@I2@", "@I3@"])
		self.assertCountEqual(grandparents, ["@I19@"])
		self.assertCountEqual(grandchildren, ["@I8@", "@I10@", "@I11@"])
		self.assertCountEqual(siblings, ["@I12@", "@I13@"])
		self.assertCountEqual(cousins, ["@I24@"])
		self.assertCountEqual(second_cousins, ["@I30@"])
		self.assertCountEqual(oncles_and_aunts, ["@I22@", "@I23@"])
		self.assertCountEqual(siblings_of_grandparents, ["@I28@"])
		self.assertCountEqual(cousins_of_parents, ["@I29@"])
		self.assertCountEqual(nephews_and_nieces, ["@I14@", "@I15@", "@I16@"])
		self.assertCountEqual(grandchildren_of_siblings, ["@I17@"])
		self.assertCountEqual(children_of_cousins, ["@I25@"])
		# when both parent are defined:
		all_siblings = self.linker.get_relatives_ref("@I7@", 0, 1)
		self.assertCountEqual(all_siblings, ["@I6@", "@I41@"])

	def test_get_by_degree(self) -> None:
		# based on https://heirbase.com/degrees_of_kinship_chart/
		self.assertCountEqual(self.linker.get_by_degree_ref("@I1@", 0), ["@I1@"])
		self.assertCountEqual(self.linker.get_by_degree_ref("@I1@", 1), ["@I6@", "@I7@", "@I41@", "@I2@", "@I3@"])
		self.assertCountEqual(self.linker.get_by_degree_ref("@I1@", 4), ["@I17@", "@I24@", "@I28@", "@I21@"])
		self.assertCountEqual(self.linker.get_by_degree_ref("@I1@", 7), ["@I27@", "@I31@", "@I36@"])
		self.assertCountEqual(self.linker.get_by_degree_ref("@I1@", 11), ["@I40@"])

if __name__ == '__main__':
	unittest.main()
