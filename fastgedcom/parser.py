"""Functions to parse gedcom files into :py:class:`.Document`.

On module import, register the ansel and gedcom codecs from the `ansel python library
<https://pypi.org/project/ansel/>`_.
"""

from typing import Iterable
from dataclasses import dataclass
from pathlib import Path

import ansel  # type: ignore[import]

from .base import Document, TrueLine, XRef

ansel.register()

class ParsingError(Exception):
	"""Error raise by :py:func:`.strict_parse`."""

class NothingParsed(ParsingError):
	"""Raised by :py:func:`.strict_parse` when the resulting document is empty."""

class ParsingWarning():
	"""Base warning class."""

@dataclass
class LineParsingWarning(ParsingWarning):
	"""Warn about a line with a single word.
	There should be at least a line level and a tag."""
	line_number: int
	line_content: str

@dataclass
class DuplicateXRefWarning(ParsingWarning):
	"""Warn about a cross-reference identifier that is defined twice."""
	xref: XRef

@dataclass
class LevelInconsistencyWarning(ParsingWarning):
	"""Warn about a line without correct parent line."""
	line_number: int

@dataclass
class LevelParsingWarning(ParsingWarning):
	"""Warn about an unparsable line level."""
	line_number: int

@dataclass
class EmptyLineWarning(ParsingWarning):
	"""Warn about an empty line."""
	line_number: int

@dataclass
class CharacterInsteadOfLineWarning(ParsingWarning):
	"""Warn about the presents of a 1-character-long line.
	This happens when the object parsed is an iterable on characters,
	whereas an iterable on lines is expected."""
	line_number: int

def parse(lines: Iterable[str]) -> tuple[Document, list[ParsingWarning]]:
	"""Parse the text input to create the
	:py:class:`.Document` object.

	List of possible :py:class:`.ParsingWarning`:

	* :py:class:`.LineParsingWarning`
	* :py:class:`.DuplicateXRefWarning`
	* :py:class:`.LevelInconsistencyWarning`
	* :py:class:`.LevelParsingWarning`
	* :py:class:`.EmptyLineWarning`
	* :py:class:`.CharacterInsteadOfLineWarning`

	Only :py:class:`.CharacterInsteadOfLineWarning` stops the parsing. If
	other warnings occur, the parsing continues with the next line.
	"""
	document = Document()
	warnings: list[ParsingWarning] = []
	line_number = 0
	parent_lines: list[TrueLine] = []
	for line in lines:
		line_number += 1
		line_info = line.rstrip().split(' ', 2)
		try:
			if len(line_info) == 3:
				parsed_line = TrueLine(int(line_info[0]), line_info[1], line_info[2], [])
			elif len(line_info) == 2:
				parsed_line = TrueLine(int(line_info[0]), line_info[1], "", [])
			elif line_info == [""]:
				warnings.append(EmptyLineWarning(line_number))
				continue
			else:
				if len(line) == 1:
					warnings.append(CharacterInsteadOfLineWarning(line_number))
					break
				warnings.append(LineParsingWarning(line_number, line))
				continue
		except ValueError:
			warnings.append(LevelParsingWarning(line_number))
			continue
		if parsed_line.level == 0:
			parent_lines = [parsed_line]
			if parsed_line.tag in document.records:
				warnings.append(DuplicateXRefWarning(parsed_line.tag))
			document.records[parsed_line.tag] = parsed_line
		else:
			while parent_lines and parsed_line.level <= parent_lines[-1].level:
				parent_lines.pop(-1)
			if len(parent_lines) == 0:
				warnings.append(LevelInconsistencyWarning(line_number))
			else:
				parent_lines[-1].sub_lines.append(parsed_line)
				parent_lines.append(parsed_line)
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
			if "�" in f.read(): raise UnicodeError
	except UnicodeError: pass
	else: return "utf-8-sig"
	try:
		with open(file, "r", encoding=None) as f:
			for line in f:
				if line.startswith("1 CHAR "):
					if "ansel" in line.lower(): return "gedcom"
					return line[7:-1] # tested with "ansi"
	except UnicodeError: pass
	try:
		with open(file, "r", encoding="utf-16") as f:
			if "�" in f.read(): raise UnicodeError
	except UnicodeError: pass
	else: return "utf-16"
	return None

def strict_parse(file: str | Path) -> Document:
	"""Open and parse the gedcom file.
	Return the :py:class:`.Document` representing the gedcom file.

	Raise :py:exc:`.ParsingError` when a error occurs in the parsing process.
	Raise :py:exc:`.NothingParsed` when the input is empty or isn't gedcom.
	"""
	with open(file, "r", encoding=guess_encoding(file)) as f:
		document, warnings = parse(f)
	if warnings: raise ParsingError(warnings)
	if len(document.records) == 0: raise NothingParsed()

	return document
