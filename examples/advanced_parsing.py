from fastgedcom.parser import guess_encoding, parse, strict_parse

file_pathname = "../my_gedcom.ged"

###############################################################################
# Minimal form
###############################################################################

document = strict_parse(file_pathname)


###############################################################################
# Indulgent parsing + Choice of the encoding
###############################################################################

encoding = guess_encoding(file_pathname)
print(file_pathname, "will be decoded using the", encoding, "codec.")
with open("../my_gedcom.ged", "r", encoding=encoding) as file:
	document, warnings = parse(file)
if warnings: print("Parsing warnings:", *warnings, "\n", sep="\n")


###############################################################################
# String parsing
###############################################################################

minimal_gedcom_text = """
0 HEAD
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 TRLR
"""
document, warnings = parse(minimal_gedcom_text.strip().splitlines())
if warnings: print("Parsing warnings:", *warnings, "\n", sep="\n")

from io import StringIO

gedcom_text = StringIO("0 HEAD\n1 GEDC\n2 VERS 5.5\n1 CHAR UTF-8\n0 @I1@ INDI\n1 NAME éàç /ÉÀÇ/\n2 SURN ÉÀÇ\n2 GIVN éàç\n1 SEX M")
document, warnings = parse(gedcom_text)
if warnings: print("Parsing warnings:", *warnings, "\n", sep="\n")


###############################################################################
# Handling warnings
###############################################################################
gedcom_with_empty_lines = """
0 HEAD
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8

...

0 TRLR
"""
document, warnings = parse(gedcom_with_empty_lines.splitlines())

from fastgedcom.parser import (ParsingError,
                               DuplicateXRefWarning, EmptyLineWarning,
                               LineParsingWarning)

for warning in warnings:
	if isinstance(warning, EmptyLineWarning):
		# Empty lines could be ok.
		pass
	elif isinstance(warning, LineParsingWarning):
		# We ignore lines that isn't [integer word phrase].
		print("Line not parsed:", warning.line_content)
	elif isinstance(warning, DuplicateXRefWarning):
		# The record is overwritten. Let's delete the one that has been kept.
		del document.records[warning.xref]
	else:
		# Other warnings are unwanted.
		raise ParsingError(warning)

