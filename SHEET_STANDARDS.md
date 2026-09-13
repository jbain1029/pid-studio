# P&ID sheet conventions and standards scope

The sheet preview, PDF, PNG, and print output use one original engineering drawing template. It is industry-informed, **not certified ISO or ISA compliance**. Standards were identified from official public scope descriptions on 2026-09-11; their licensed normative requirements and symbol tables were not reproduced or exhaustively audited.

## Relevant references

- [ISO 10628-1:2014](https://www.iso.org/standard/51840.html) addresses classification, content, representation and drafting of chemical/petrochemical flow diagrams. It is the relevant diagram-level reference, not a guarantee that an arbitrary drawing has adequate engineering content.
- [ISO 7200:2004](https://www.iso.org/standard/35446.html) addresses technical document titleblock/header data. The app supplies document identity, revision, responsibility and status fields for that purpose, using its own layout.
- [ISO 5457:1999](https://www.iso.org/standard/29017.html) addresses technical drawing sheet sizes/layout; its official page also lists Amendment 1:2010. The app retains A4/A3 and ANSI B/D landscape sizes. ANSI sizes are not presented as ISO paper sizes.
- [ISA5.1 committee scope](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa5-1) identifies ANSI/ISA-5.1-2024 as the instrumentation/control identification reference. The app's simplified component artwork and generic signal line are not a complete implementation of that standard.

## What is implemented

File > Drawing settings controls drawing number, revision, owner/organization, project, preparer, checker, approver, issue status/date, set sheet number/count, optional project drafting specification, and general notes. Existing files remain readable; these are ordinary string metadata values.

- Lower-right ruled titleblock with explicit responsibility and document-control cells.
- Fixed **NOT TO SCALE** designation because this is a connectivity schematic, not a dimensioned fabrication/layout drawing.
- Unspecified status displays **DRAFT - NOT FOR CONSTRUCTION**. This is a conservative app default, not a statement required by every standard. An approval name is user-entered text, not an electronic signature or verified authorization.
- Physical frame margins: 20 mm on the left for binding and 10 mm on other edges. These are this app's chosen template dimensions; exact standards conformance has not been audited. No zone grid, folding marks, or revision-change table is claimed.
- Visible legend matching the renderer: solid process/fluid lines; dashed generic instrument/control signals. The dashed style does **not** identify pneumatic, electrical, hydraulic or software media. Project-specific media conventions are not implemented.
- Crossings alone have no connectivity. Use a junction component and explicit port connections for a branch. The file's endpoint references determine topology, not apparent line contact.
- Separate general notes area. Long metadata is measured and wrapped; excessive content is rejected before overwriting an export rather than silently clipped.
- Sheet number/count identify this single drawing within a user-managed drawing set. They do not create multiple pages or cross-sheet links. Values must be positive integers up to 9999 and number must not exceed count. Blank values default to 1.

## Engineering review still required

Before issue, verify the applicable plant/project drafting specification, component/instrument identification, all process and signal connections, line numbering/specification/size, service, valve fail/normal state, safeguards, notes and revision/approval status. Custom component artwork and generic tags need project review. Entering a standard name in Project drafting specification does not certify compliance.

Automatic routing, sheet fitting and diagnostics do not validate process safety, sizing, fluid behavior, construction readiness, instrument function codes, minimum printed symbol/text sizes, or every licensed standard requirement. Fit-to-sheet can reduce component labels on dense drawings; inspect the actual intended paper output and split the drawing into separate files when needed.
