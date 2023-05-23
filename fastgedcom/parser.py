from typing import IO
from pathlib import Path

from .base import Gedcom, GedcomLine
from .structure import XRef

import ansel
ansel.register()

class ParsingError(Exception): pass

class ParsingWarning():
	"""Base warning class."""

class LineParsingWarning(ParsingWarning):
	"""Warn about an unparsable line."""
	def __init__(self, line_number: int, line_content: str) -> None:
		self.line_number = line_number
		self.line_content = line_content
	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__} line {self.line_number}>"

class DuplicateParsingWarning(ParsingWarning):
	"""Warn about a level 0 reference that is present twice."""
	def __init__(self, xref: XRef) -> None:
		self.xref = xref
	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__} xref={self.xref}>"

def parse(readable_lines: IO[str]) -> tuple[Gedcom, list[ParsingWarning]]:
	"""Parser for gedcom documents to create the Gedcom class."""
	gedcom = Gedcom()
	warnings: list[ParsingWarning] = []
	line_number = 0
	try:
		parent_lines: list[GedcomLine] = []
		for line in readable_lines:
			line_number += 1
			line_info = line.rstrip().split(' ', 2)
			if len(line_info) == 3:
				parsed_line = GedcomLine(int(line_info[0]), line_info[1], line_info[2], [])
			elif len(line_info) == 2:
				parsed_line = GedcomLine(int(line_info[0]), line_info[1], None, [])
			else:
				warnings.append(LineParsingWarning(line_number, line))
				continue
			if parsed_line.level == 0:
				parent_lines = [parsed_line]
				if parsed_line.tag in gedcom.level0_index:
					warnings.append(DuplicateParsingWarning(parsed_line.tag))
				gedcom.level0_index[parsed_line.tag] = parsed_line
			else:
				while parent_lines and parsed_line.level <= parent_lines[-1].level:
					parent_lines.pop(-1)
				if len(parent_lines) == 0: raise ParsingError("Inconsistent use of line levels")
				parent_lines[-1].sub_rec.append(parsed_line)
				parent_lines.append(parsed_line)
	except UnicodeDecodeError:
		raise ParsingError(line_number, "UnicodeDecodeError")
	except ValueError: # raised on int parsing error
		raise ParsingError(line_number, "Line parsing failed")
	__build_parents(gedcom)
	return (gedcom, warnings)

def __build_parents(gedcom: Gedcom) -> None:
	for fam_record in gedcom.level0_index.values():
		if fam_record.payload != "FAM": continue
		father = mother = None
		children = []
		for record in fam_record.sub_rec:
			if record.payload is None: continue
			if record.tag == "CHIL":
				children.append(record.payload)
			elif record.tag == "HUSB":
				father = record.payload
				if father in gedcom.unions:
					gedcom.unions[father].append(fam_record.tag)
				else: gedcom.unions[father] = [fam_record.tag]
			elif record.tag == "WIFE":
				mother = record.payload
				if mother in gedcom.unions:
					gedcom.unions[mother].append(fam_record.tag)
				else: gedcom.unions[mother] = [fam_record.tag]
		for child in children:
			gedcom.parents[child] = (father, mother)


def guess_encoding(file: str | Path) -> str | None:
	try:
		with open(file, "r", encoding="utf-8-sig") as f:
			f.read()
	except UnicodeDecodeError: pass
	else: return "utf-8-sig"
	try:
		with open(file, "r", encoding=None) as f:
			for line in f:
				if line.startswith("1 CHAR "):
					if "ansel" in line.lower(): return "gedcom"
					return line[7:-1] # tested with "ansi"
	except UnicodeDecodeError: pass
	try:
		with open(file, "r", encoding="utf-16") as f:
			f.read()
	except UnicodeDecodeError: pass
	else: return "utf-16"
	return None

