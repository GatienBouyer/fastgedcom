from typing import IO

from .gedcom_base import Gedcom, GedcomLine


def export(gedcom: Gedcom, s: IO[str]) -> None:
	for line in gedcom:
		s.write(str(line)+"\n")
		s.writelines(map(str, line.all_sub_rec_recursive()))

class GedcomInconsistency():
	def __init__(self, record: GedcomLine) -> None:
		self.record = record
	
	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__} '{self.record}'>"

def check_integrity(gedcom: Gedcom) -> list[GedcomInconsistency]:
	"""Check the consistency of the document,
    its compliancy with the FamilySearch GEDCOM 7.0 standard."""
	""" @TODO

	Checks to be done:
	Errors:
	- there is gedcom value when tag requires it (CHIL, HUSB, WIFE)
		> A structure must have either a non-empty payload or at least 1 substructure.
		> Pseudo-structure needn't (pseudo-structures are HEAD, TRLR and CONT)
	- levels are consistents (level 2 inside a level 1 - not directly inside a level 0)
	- referenced value don't exist (e.g. reference to a @S1@ that doesn't exist)
		> Pointers to a removed structure should be replaced with a void ref
	- gedcom structure is respected (the required substructure)
	- verify interdiction for 2 father or 2 mother

	Warnings:
	- Record that is not used
		> A record to which no structures point may have a cross-reference identifier, but does not
	need to have one
	- non conventionnal tags
	"""
	return []
