from typing import Literal, TypeAlias

SubmRef: TypeAlias = str
"""The cross-reference identifier of type '@SUB1@' or '@U1@' for a submitter of the document."""
SubnRef: TypeAlias = str
"""Deprecated. The cross-reference identifier of type '@SUB1@' for a submission."""
IndiRef: TypeAlias = str
"""The cross-reference identifier of type '@I1@' for an individual."""
FamRef: TypeAlias = str
"""The cross-reference identifier of type '@F1@' for a family."""
SNoteRef: TypeAlias = str
"""The cross-reference identifier of type '@N1@' for a shared note."""
SourRef: TypeAlias = str
"""The cross-reference identifier of type '@S1@' for a source document."""
RepoRef: TypeAlias = str
"""The cross-reference identifier of type '@R1@' for a repository (an archive)."""
ObjeRef: TypeAlias = str
"""The cross-reference identifier of type '@O1@' for an object (e.g. an image)."""

XRef: TypeAlias = SubmRef | SubnRef | IndiRef | FamRef | SNoteRef | SourRef | RepoRef | ObjeRef
"""The cross-reference identifier indicates a record to which payloads may point. """

VoidRef: TypeAlias = Literal['@VOID@']
"""A pointer used for unknown value and to have something in the payload.
e.g.: in a family record, a line '2 CHIL @VOID@' indicates a placeholder for an unknown child."""

Pointer: TypeAlias = XRef | VoidRef
"""Generic pointer that is used in the payload to reference an existing record or a non-existing one."""

