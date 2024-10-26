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
