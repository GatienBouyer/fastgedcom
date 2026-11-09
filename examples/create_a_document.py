from fastgedcom.base import Document, TrueLine

# New blank document
gedcom = Document()

# Create new records
gedcom.records["@I1@"] = TrueLine(0, "@I1@", "INDI")
gedcom.records["@F1@"] = TrueLine(0, "@F1@", "FAM")

# Fill up a record
indi = TrueLine(0, "@I2@", "INDI")
indi.sub_lines.extend([
    TrueLine(1, "SEX", "M"),
    TrueLine(1, "NAME", "John /Doe/", [
        TrueLine(2, "SURN", "Doe"),
        TrueLine(2, "GIVN", "John"),
    ]),
    TrueLine(1, "FAMS", "@F1@"),
])
gedcom.records["@I2@"] = indi

###################################################
#                    WARNING !                    #
# This gedcom doesn't conform with the standard.  #
# E.g., it misses some fields as HEAD and TRLR.   #
###################################################

print(gedcom.get_source())

###############################################################################
# Use the built-in convenient methods
###############################################################################

new_indi = gedcom.get_or_create("@I3@", "INDI")
new_indi.get_sub_line_or_create("SEX").payload = "M"
name = new_indi.get_sub_line_or_create("NAME")
name.payload = "John /DOE/"
name.get_sub_line_or_create("SURN").payload = "DOE"
name.get_sub_line_or_create("GIVN").payload = "John"

new_indi.get_sub_line_or_create("BIRT").get_sub_line_or_create("DATE").payload = "1 JAN 2000"

print(gedcom.get_source())
