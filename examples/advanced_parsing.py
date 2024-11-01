from fastgedcom.parser import (
    DuplicateXRefWarning, EmptyLineWarning, LevelInconsistencyWarning,
    MalformedError, guess_encoding, parse, strict_parse
)

file_pathname = "../my_gedcom.ged"

###############################################################################
# Minimal form
###############################################################################

document = strict_parse(file_pathname)


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
if warnings:
    print("Parsing warnings:", *warnings, "\n", sep="\n")


###############################################################################
# Indulgent parsing + choice of the encoding
###############################################################################

encoding = guess_encoding(file_pathname)
print(file_pathname, "will be decoded using the", encoding, "codec.")

with open(file_pathname, "r", encoding=encoding) as file:
    document, warnings = parse(file)
if warnings:
    print("Parsing warnings:", *warnings, "\n", sep="\n")


###############################################################################
# Handling warnings
###############################################################################

gedcom_with_empty_lines = """
0 HEAD
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8


0 TRLR
"""
document, warnings = parse(gedcom_with_empty_lines.splitlines())


for warning in warnings:
    if isinstance(warning, EmptyLineWarning):
        # We can accept empty lines.
        pass
    elif isinstance(warning, DuplicateXRefWarning):
        # Two records (individuals, families, etc.) have the same reference.
        # The first record is overwritten by the second one.
        # Let's delete the one that has been kept.
        del document.records[warning.xref]
    elif isinstance(warning, LevelInconsistencyWarning):
        # Line levels are not coherent.
        # We can keep the gedcom as is and print a warning
        print(f"Error in levels near the line {warning.line_number}: {warning.line_content}")
    else:
        # We can consider other types of warning as fatal.
        raise MalformedError([warning])
