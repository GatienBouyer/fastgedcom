"""Functions to parse gedcom files into :py:class:`.Document`.

On module import, register the ansel and gedcom codecs from the `ansel python library
<https://pypi.org/project/ansel/>`_.
"""

from typing import Iterable
from dataclasses import dataclass
from pathlib import Path

import ansel  # type: ignore[import-untyped]

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

    This function is based on the following GEDCOM guidelines:

    A gedcom should precise its encoding in the header under the tag CHAR.
    However, indication of that field are often misleading. For example:
    ANSEL refers to the gedcom version of the ansel charset. The use of a BOM
    mark is recommended, but its presence is not stated in the CHAR field,
    and is not automatically detected by Python. The value of UNICODE refers
    to UTF-16, but Python doesn't have this alias out of the box.
    """
    # check BOM mark to deduce UTF family encodings
    # see http://unicode.org/faq/utf_bom.html#bom4
    with open(file, "rb") as f:
        first_bytes = f.read(4)
    if first_bytes[:3] == b"\xef\xbb\xbf":
        # UTF-8
        # The presence of the BOM mark must be specified.
        # With "utf-8-sig, Python removes the BOM mark when reading the file.
        return "utf-8-sig"
    if first_bytes[:2] == b"\xff\xfe":
        # UTF-16, little-endian
        # With "utf_16", Python removes the BOM mark when reading the file.
        return "utf_16"
    if first_bytes[:2] == b"\xfe\xff":
        # UTF-16, big-endian
        # With "utf_16", Python removes the BOM mark when reading the file.
        return "utf_16"
    if first_bytes == b"\xff\xfe\x00\x00":
        # UTF-32, little-endian
        # With "utf_32", Python removes the BOM mark when reading the file.
        return "utf_32"
    if first_bytes == b"\x00\x00\xfe\xff":
        # UTF-32, big-endian
        # With "utf_32", Python removes the BOM mark when reading the file.
        return "utf_32"
    # Try non-utf encodings and loog at the 0 HEAD > 1 CHAR gedcom field
    encodings = (
        "utf-8",
        "ansel",
        "iso8859-1",
    )
    for encoding in encodings:
        try:
            with open(file, "r", encoding=encoding) as f:
                for line in f:
                    if line.startswith("1 CHAR "):
                        stated_encoding = line[7:-1].lower()
                        if stated_encoding == "ansel":
                            return "gedcom"
                        return stated_encoding
        except UnicodeError:
            pass
    return None


def strict_parse(file: str | Path) -> Document:
    """Open and parse the gedcom file.
    Return the :py:class:`.Document` representing the gedcom file.

    Raise :py:exc:`.ParsingError` when a error occurs in the parsing process.
    Raise :py:exc:`.NothingParsed` when the input is empty or isn't gedcom.
    """
    with open(file, "r", encoding=guess_encoding(file)) as f:
        document, warnings = parse(f)
    if warnings:
        raise ParsingError(warnings)
    if len(document.records) == 0:
        raise NothingParsed()

    return document
