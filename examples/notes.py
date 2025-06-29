from fastgedcom.parser import parse

# Sections
# - Note one multiple lines
# - Several notes
# - Shared notes
#   - for gedcom v5
#   - for gedcom v7
# - Sublines of notes
# - Notes can be anywhere


# Notes register any textual data. It can be an additional information
# about a person's life or it can be a researcher note about the
# registries you already searched through and find nothing.

# Notes on several lines are split into 'CONT' sublines.
# Use the payload_with_cont property instead of the payload attribut
# to read notes.

gedcom_notes, _ = parse(
	"""0 HEAD
	0 @I1@ INDI
	1 NAME John /DOE/
	1 BIRT
	2 DATE 1952
	1 DEAT
	2 DATE 1952
	1 NOTE John died at birth.
	2 CONT This left his parent in great despair.
	2 CONT They needed a year to recover.
	0 TRLR
	""".splitlines(),
)
person = gedcom_notes["@I1@"]
note = person > "NOTE"
print(f"Note about John:\n{note.payload_with_cont}\n")


# Several notes
# There is not limit on the number of notes there can be.
# However, most genealogy software use only one note, which regroup all the information.

gedcom_several_notes, _ = parse(
	"""
	0 @I1@ INDI
	1 NAME John /DOE/
	1 NOTE I find John's birth record.
	1 NOTE I didn't find John's marriage.
	1 NOTE I didn't find John's portrait.
	""".splitlines(),
)
person = gedcom_several_notes["@I1@"]
for i, note in enumerate(person >> "NOTE"):
	print(f"Note n°{i}: {note.payload_with_cont}")
print("")


# Shared notes
# Shared notes allow several object (e.g. person) to use the same note.
# Nota: Introduced in gedcom version 5, there was modified in version 7: replace 'NOTE' by 'SNOTE'.

gedcom_v5_shared_notes_content, _ = parse(
	"""
	0 @I1@ INDI
	1 NAME John /DOE/
	1 NOTE @N1@
	0 @I2@ INDI
	1 NAME Jane /DOE/
	1 NOTE @N1@
	0 @N1@ NOTE John and Jane lived together.
	""".splitlines(),
)
person = gedcom_v5_shared_notes_content["@I1@"]
for note in person >> "NOTE":
	if note.payload.startswith("@") and note.payload.endswith("@"):
		# This note is a shared note
		shared_note = gedcom_v5_shared_notes_content[note.payload]
		shared_note_content = shared_note.payload_with_cont[len("NOTE "):]
		print("Shared note (gedcom v5):", shared_note_content)

gedcom_v7_shared_notes_content, _ = parse(
	"""
	0 @I1@ INDI
	1 NAME John /DOE/
	1 SNOTE @N1@
	0 @I2@ INDI
	1 NAME Jane /DOE/
	1 SNOTE @N1@
	0 @N1@ SNOTE John and Jane lived together.
	""".splitlines(),
)
person = gedcom_v7_shared_notes_content["@I1@"]
for note in person >> "SNOTE":
	if note.payload.startswith("@") and note.payload.endswith("@"):
		# This note is a shared note
		shared_note = gedcom_v7_shared_notes_content[note.payload]
		shared_note_content = shared_note.payload_with_cont[len("SNOTE "):]
		print("Shared note (gedcom v7):", shared_note_content)


# Sublines of a note
# Notes can have translation and sources. Notes can also be in other format, e.g. markdown.
gedcom_note_sublines, _ = parse(
	"""
	0 @I1@ INDI
	1 NOTE # It's me!
	2 CONT Me, the author!
	2 CONT :)
	2 MIME text/markdown
	2 LANG EN
	2 TRAN C'est moi ! Moi, l'auteur ! :)
	3 MIME text/plain
	3 LANG FR
	2 SOUR @S1@
	0 @S1@ SOUR
	1 TITL Me
	""".splitlines(),
)
note = gedcom_note_sublines["@I1@"] > "NOTE"
print("\nNote:")
print("Language:", note >= "LANG")
print("Format:", note >= "MIME")
print(f"Content:\n{note.payload_with_cont}")
for translation in note >> "TRAN":
	print("Translation: ---")
	print("Language:", translation >= "LANG")
	print("Format:", translation >= "MIME")
	print(f"Content:\n{translation.payload_with_cont}")
for source in note >> "SOUR":
	print("Source:", source.payload)


# Notes can store additional information about:
# a person, a family, an event (birth, marriage, ...), a person name, a place, a source, etc.
# It is very unlikely that you will need of all those note kinds.

gedcom_note_kinds, _ = parse("""0 HEAD
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
1 NOTE This gedcom contains notes in various places.
1 SUBM @SUB1@
0 @SUB1@
1 NAME Me
1 NOTE I am a genealogy fan who help building this document. Contact me at XXX.
0 @I1@ INDI
1 NAME John /DOE/
2 NOTE Everyone called him Jon-do.
1 BIRT
2 DATE 1900
2 NOTE John was 5kg at birth and 50cm tall.
2 SOUR @S1@
1 BAPL
3 PLAC St Marie church, Lost City, Country
4 NOTE John often went to this church to confess.
3 NOTE John was baptized.
1 NO MARR
3 NOTE John did married his partner according to his daughter.
1 FAMC @F1@
2 NOTE In my papers, I found the birth record of John. :)
1 FAMS @F2@
2 NOTE I know, John had a partner, but I did't find any document about it.
2 CONT Maybe I will have better luck next time.
1 ASSO @I2@
2 ROLE FRIEND
2 NOTE Best friend of John. They met during their military service.
1 NOTE John is the main person of this gedcom.
1 CHAN
2 DATE 1 Jan 2020
3 TIME 12:34:56
2 NOTE Fix a typo in a sentence of a note.
0 @O1@ OBJE
1 FILE C:\\Users\\Me\\Documents\\John DOE family tree\\docs\\John birth record.png
1 NOTE The birth record of John.
0 @S1@ SOUR
1 DATA
2 NOTE The original birth record of John is intact and kept by Jane, John's daughter.
1 REPO @R1@
2 NOTE Jane send me a photo of John's birth record.
1 OBJE @O1@
1 NOTE Source document for the birth of John.
0 @R1@ REPO
1 NAME Jane DOE
1 NOTE Jane, John's daughter, have all documents about John's life.
0 @F1@ FAM
1 FAMC @I1@
1 NOTE The family with the parents of John.
0 TRLR
""".splitlines())
print("\nNote kinds")
# Here, I use 'payload' instead 'payload_with_cont' for conciseness,
# but you should always use 'payload_with_cont' for notes.
# Also there can be several lines of each type compared to this example.
print("Gedcom note:", (gedcom_note_kinds["HEAD"]) >= "NOTE")
print("Submitter note:", gedcom_note_kinds["@SUB1@"] >= "NOTE")
print("Person note:", gedcom_note_kinds["@I1@"] >= "NOTE")
print("Person name note:", (gedcom_note_kinds["@I1@"] > "NAME") >= "NOTE")
print("Event note:", (gedcom_note_kinds["@I1@"] > "BIRT") >= "NOTE")
print("LDS event note:", (gedcom_note_kinds["@I1@"] > "BAPL") >= "NOTE")
print("Place note:", ((gedcom_note_kinds["@I1@"] > "BAPL") > "PLAC") >= "NOTE")
print("No event note:", (gedcom_note_kinds["@I1@"] > "NO") >= "NOTE")
print("Parent family note:", (gedcom_note_kinds["@I1@"] > "FAMC") >= "NOTE")
print("Spouse family note:", (gedcom_note_kinds["@I1@"] > "FAMS") >= "NOTE")
print("Association note:", (gedcom_note_kinds["@I1@"] > "ASSO") >= "NOTE")
print("Change note:", (gedcom_note_kinds["@I1@"] > "CHAN") >= "NOTE")
print("Media note:", gedcom_note_kinds["@O1@"] >= "NOTE")
print("Source note:", gedcom_note_kinds["@S1@"] >= "NOTE")
print("Source data note:", (gedcom_note_kinds["@S1@"] > "DATA") >= "NOTE")
print("Repository link note:", (gedcom_note_kinds["@S1@"] > "REPO") >= "NOTE")
print("Repository note:", gedcom_note_kinds["@R1@"] >= "NOTE")
print("Family note:", gedcom_note_kinds["@F1@"] >= "NOTE")
