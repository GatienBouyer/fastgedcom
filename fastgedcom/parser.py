"""Functions to parse gedcom files into :py:class:`.Document`.

On module import, register the ansel and gedcom codecs from the `ansel python library
<https://pypi.org/project/ansel/>`_.
"""

from typing import IO
from pathlib import Path

import ansel

from .base import Document, TrueLine, XRef

ansel.register()

class ParsingError(Exception):
	"""Error raised by :py:func:`.parse`."""

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
	"""Warn about a cross-reference identifier that is defined twice."""
	def __init__(self, xref: XRef) -> None:
		self.xref = xref
	def __repr__(self) -> str:
		return f"<{self.__class__.__qualname__} xref={self.xref}>"

def parse(readable_lines: IO[str]) -> tuple[Document, list[ParsingWarning]]:
	"""Parse the text input to create the
	:py:class:`.Document` object.

	For major failure, raise :py:exc:`.ParsingError`.

	For minor failure, append a :py:class:`.ParsingWarning` to the returned list.

	Non-exhaustive list of possible failures:

	* (Major) First line word can't be converted to an integer.
	* (Minor) Line with a single word. :py:class:`.LineParsingWarning`
	* (Minor) A cross-reference identifier is defined twice. :py:class:`.DuplicateParsingWarning`
	* (Major) Inconsistent use of line level.
	"""
	document = Document()
	warnings: list[ParsingWarning] = []
	line_number = 0
	try:
		parent_lines: list[TrueLine] = []
		for line in readable_lines:
			line_number += 1
			line_info = line.rstrip().split(' ', 2)
			if len(line_info) == 3:
				parsed_line = TrueLine(int(line_info[0]), line_info[1], line_info[2], [])
			elif len(line_info) == 2:
				parsed_line = TrueLine(int(line_info[0]), line_info[1], "", [])
			elif line_info == [""]:
				# empty line is ok
				continue
			else:
				warnings.append(LineParsingWarning(line_number, line))
				continue
			if parsed_line.level == 0:
				parent_lines = [parsed_line]
				if parsed_line.tag in document.level0_index:
					warnings.append(DuplicateParsingWarning(parsed_line.tag))
				document.level0_index[parsed_line.tag] = parsed_line
			else:
				while parent_lines and parsed_line.level <= parent_lines[-1].level:
					parent_lines.pop(-1)
				if len(parent_lines) == 0: raise ParsingError("Inconsistent use of line levels")
				parent_lines[-1].sub_lines.append(parsed_line)
				parent_lines.append(parsed_line)
	except ValueError as err: # raised on int parsing error
		raise ParsingError(line_number, "Line parsing failed") from err
	return (document, warnings)

def guess_encoding(file: str | Path) -> str | None:
	"""Return the guessed encoding of the ``file``. None if unknown.

	No proper detection of the encoding of a file is ever possible.

	This function is based on the following guidelines:

	A gedcom should precise its encoding in the header under the tag CHAR.
	However, indication of that field are often misleading. For example:
	ANSEL refers to the gedcom version of the ansel charset.
	The BOM mark is never mention and isn't automatically detected by Python.
	UNICODE is not recognized by Python and should be manually set to UTF-16.
	"""
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

