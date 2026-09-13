# Foot-valve direction and inline relief follow-up

2026-09-12. Read-only follow-up during executable verification. No production edits. Purpose: find inspectable primary-source **symbol figures**, not infer symbol validity from product descriptions or cutaway drawings.

## Findings and next correction

| Component | Evidence-backed result | Concrete recommendation |
|---|---|---|
| `foot_valve` | A primary vendor P&ID legend was found with a foot-valve glyph connected above its seat: upright triangle below a horizontal seat and upper connection. Current app has the opposite triangle/seat arrangement above its lower strainer. The vendor sheet does not show a flow arrow or integrated strainer, so this is not a complete proof of the existing assembly's allowed-flow convention. | Adopt the documented upright foot-valve body as a **declared project convention**, keeping the app's bottom strainer and existing bottom suction/top discharge ports. Record the added strainer as composition, not an exact copy of the reference. Do not claim the old triangle was universally forbidden. |
| `relief_valve` | Primary manufacturer hydraulic symbols substantiate a square/arrow/spring *family*, but not the app's exact spring-over-box/diagonal-arrow form. A directly inspected DOE **inline** process-P&ID relief alternative is available; an angle-only replacement is not necessary. | Replace the unresolved box graphic with the DOE inline alternative, preserving left inlet/right outlet. Do not label it ISO-certified or infer a fail state beyond the cited glyph. |

## Foot valve: inspected primary figures

### IXOM, High Level MIEX pre-treatment P&ID legend

Source: [Town of High Level, January 13, 2025 council agenda package](https://www.highlevel.ca/AgendaCenter/ViewFile/Agenda/_01132025-351), PDF page **118**, vendor drawing **NAXXXX-03-00-002**, revision B, sheet 1 of 11, titled *Piping & Instrumentation Diagram / P&ID Symbols*, project *75 LPS High Level, AB / MIEX Pre-Treatment*. IXOM is the drawing author; the municipality hosts the primary project submission. Revision history shows preliminary updates dated 13 November 2024. This is project evidence, not a normative general standard. The sheet itself includes restrictions on reuse and is preliminary: do not redistribute the source drawing as app artwork or imply it approves another installation.

Visually inspected the complete sheet and a higher-resolution render of its **Valve Symbols / FOOT VALVE** cell. The cell has an upper vertical connection to a horizontal seat, with an open triangular body underneath and its apex upward against the seat. It has no depicted strainer or lower pipe stub. The current application after its continuity repair has triangle points (-13,-18),(0,0),(13,-18), seat at y=0, and strainer y=7..25: its apex points down toward the lower seat/strainer.

The source gives an exact reference for choosing a coherent upright symbol, but the caption alone does not prove flow-direction physics for every foot-valve notation. This distinction matters: it is stronger evidence for **adopting a documented replacement** than for retroactively declaring the current pictogram prohibited.

Recommended app-space construction if authorized later: retain `discharge=[0,-40]`, `suction=[0,40]`, the existing strainer, and bounding envelope. Put the seat at y=-18, triangle vertices (-13,0),(0,-18),(13,0), upper lead from discharge to the seat, and short lower bridge from triangle base y=0 to strainer top y=7. This is a proposed composition using the vendor's orientation, not a claim that its legend includes our full assembly. Preserve explicit suction-to-discharge metadata; never infer that direction from line click order.

### Opus DaytonKnight / Sunshine Coast Regional District

Source: [Egmont Cove Water System Upgrade record drawings](https://www.scrd.ca/wp-content/uploads/2025/11/2537030-Appendix-3-As-Built-Record-Drawings-Egmont-Water-System-Upgrade-2013-Detailed-Design-and-Engineering-%E2%80%93-Egmont-Water-Treatment-Improvements.pdf), PDF page **13**, drawing **028.199.0005**, sheet **P2**, issue D, *P&ID Standard Symbols, Equipment, Valves and Instrumentation*. The author is Opus DaytonKnight; the regional district hosts the record set. Complete sheet visually inspected, especially Valve Labelling System / FOOT VALVE and pressure-relief cells.

Its foot-valve graphic is a small rectangular diagonal form, not the IXOM triangle. It does not validate our exact integrated-strainer drawing or settle flow direction. This independent primary-project variation reinforces the need to name the adopted legend rather than assert one universal foot-valve glyph.

## Relief valve: inspected primary figures

### DOE process-P&ID alternative: recommended

Source: [DOE-HDBK-1016/1-93, Engineering Symbology, Prints, and Drawings, Volume 1](https://www.energy.gov/sites/default/files/2026-04/DOE-HDBK-1016-93_VOL1.pdf), January 1993, Module PR-02 printed page 3, PDF page **55**, **Figure 1, Valve Symbols**, RELIEF / ALTERNATIVES row. The complete figure and a high-resolution relief-row render were inspected.

The middle inline alternative has a horizontal process line, opposing valve triangles, the right triangle filled, and a curved central relief mark. It is not a plain gate valve and not our current arrow-in-box drawing. An implementation can preserve the existing two horizontal ports by drawing leads to this body; use a sampled vector curve for the central mark. Keep the right/left orientation as illustrated, and document the source alternative explicitly. Do not interpret the filled half using a separate chart's full-valve normal-state legend.

DOE also gives angle alternatives. Therefore forcing existing `relief_valve` connections into a right angle would be an unnecessary compatibility change, not a consequence of this evidence.

### Bosch Rexroth hydraulic relief symbols: family evidence only

Source: [Bosch Rexroth RE 25860/11.11, Pressure relief valves](https://apps.boschrexroth.com/products/compact-hydraulics/CH-Catalog/pdf/re25860_2011-11.pdf), printed/PDF page **2**, *Function*: the **three actual schematic symbols above the cutaways** were visually inspected. The cutaways below were not used as symbol evidence.

These show square valve envelopes with flow arrows, spring actuation at the side, identified P/T connections and pressure-control paths; variants also include additional check/damping elements. They substantiate the existence of the hydraulic square/arrow/spring family, but do not establish the exact current app geometry or justify omitting the depicted pressure-control paths. This hydraulic product source cannot by itself make the existing process-P&ID glyph an ISO-compliant PSV. Keep the current exact form unresolved rather than inflating this family resemblance into an exact match.

## Search limits and verification record

Hexagon's Smart P&ID valve listing identified a Foot Valve symbol filename, but the actual icon was inaccessible in the inspected response: not accepted as visual evidence. Parker's Catalog 0700P appeared in indexed results, but direct PDF retrieval returned access denied; no bypass was attempted. No standards were purchased. The supplied Edraw legend, prior DOE/VA inspection and the new project sheets give adequate evidence for a bounded next step without indefinite searching.

Temporary review materials are organized under `tmp/pdfs/industry-study/`: `highlevel.pdf`, `highlevel-118.png`, `highlevel-foot-detail.png`, `egmont.pdf`, `egmont-12.png`, `egmont-13.png`, `rexroth-relief.pdf`, `rexroth-relief-02.png`, and `doe-relief-detail.png`. These are research evidence only, not application deliverables. Any later implementation should update its own provenance and regression tests, render all four rotations, verify unchanged ports, and rebuild only after production changes are authorized.
