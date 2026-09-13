# PID Studio

Reports > Component legend (SVG) exports the exact component symbols used in the
current drawing, once per type, with names and recorded reference conventions.
Keep this companion legend with its matching drawing and regenerate it after
changes. It is not a standards-compliance certificate.

Local Python desktop P&ID editor. Start by double-clicking `launch.cmd`.
The isolated Python environment is installed in `.venv`; no paid service is needed.
Run `setup.cmd` to install/update dependencies and verify the local installation. Setup requires an installed Python 3 interpreter and an internet connection for dependencies; ordinary offline editing does not.

For a portable Windows executable, see [PACKAGING.md](PACKAGING.md). `build.cmd`
creates a self-contained application folder; keep its `_internal` folder beside the executable.

## Editing

- Covered component artwork now follows the supplied `pid-legend.pdf`. Hover over a component to see the selected reference entry. Existing ports are preserved; unmatched specialized components stay unchanged. See [LEGEND_REFERENCE.md](LEGEND_REFERENCE.md) for scope and adaptations.

- Component categories use small engineering-themed navigation icons in both the Toolbox and catalog browser; the expansion arrows still open subcategories. These UI icons do not replace the actual component symbols used in drawings.

- The Toolbox and component browser organize all components into expandable folders and subfolders (Process components, Valves, Piping, Instrumentation, Steam & utilities, Pressure protection, and Custom components when present). Open folders to browse; drag or double-click a component to insert it. Search finds components across all folders and temporarily opens matches; clearing search restores your previous folder layout.

- Edit > Create connection opens precise endpoint controls. Choose each component and named port, the process/signal type and label, and optional ordered X/Y routing waypoints. Right-click an existing connection > Edit connection to revise it. Add/remove/reorder points, reset automatic routing or reverse endpoints; Apply is one undoable change and Cancel leaves the drawing untouched.
- Popup menus and combo lists use an explicit light palette even when Windows is in dark mode.
- Sheet preview and exports now use a ruled engineering titleblock with owner/project, drawing/revision, prepared/checked/approved, issue status/date, drawing-set sheet numbering, NOT TO SCALE and a process/signal legend. Configure these in Drawing settings. Blank issue status defaults to DRAFT - NOT FOR CONSTRUCTION. See [SHEET_STANDARDS.md](SHEET_STANDARDS.md) for ISO/ISA reference scope and limitations; this is not a standards-compliance certificate.

- Open a drawing by dropping one local `.pid`/`.json` file onto the drawing canvas, or pass its quoted path to `launch.cmd`. The portable executable also accepts a drawing path (including dropping a file onto the executable in Explorer after rebuilding). No automatic Windows file association is installed. Missing/invalid files leave the current drawing untouched.

- The status bar reports current component/line/note counts, selection count, snap spacing and grid visibility. Grid dots use snap-spacing multiples and become coarser when zoomed out to stay readable. Notes also appear in the project outline; click one to select it on the drawing.

- To move a pipe endpoint, right-click the pipe and choose Reconnect source or Reconnect destination, then click a new port. Escape cancels. Reconnection preserves the line ID, label, type, engineering properties and route waypoints, and is undoable. An incompatible signal/process choice is rejected. If retained waypoints create a blocked route, move them or use Reset to automatic routing.

- Sketch / AI > Accepted proposal history shows locally recorded acceptance times, full accepted proposals, acknowledged checks, and content fingerprints. New API drafts also include separately captured request-time model/response IDs, reported token usage, schema/instruction/request fingerprints and the normalized image payload fingerprint. The original attachment is distinguished from the submitted PNG. These editable records travel with `.pid` files and undo together with edits; they are not signed proof of provider receipt or engineering approval. API keys, prompt text and submitted image bytes are not copied into the generation records. Offline/older proposals may have no request-time record.

- Offline edit proposals and OpenAI responses can include structured `review_findings` with source-image regions and affected draft object IDs. The review dialog highlights each area and requires each check to be acknowledged before Apply. This does not certify correctness: cancel and revise an incorrect proposal. The OpenAI adapter uses wire format v2, validated locally; live provider verification remains planned.

- File > Recover autosaved drawing lists recovery snapshots by title and local save time, shows component tags and contents, and flags invalid files. Recover copy validates the file again and opens it as an unsaved drawing. It does not delete the source snapshot; save the recovered drawing to a normal file.

- Use the Sheet preview workspace tab (or View > Sheet preview) to inspect the actual export layout, border, title block and paper proportions. Wheel zooms; drag pans; Fit page resets the view. Drawing settings can be edited from the preview. The preview is read-only and omits the tracing sketch, just like the exported sheet.

- Right-click components, piping, or the canvas for editing commands; right-click a waypoint to remove it.
- With the drawing focused, Ctrl+A selects all. Arrow keys move selected components/notes by the configured snap spacing (one unit with snap disabled); Shift moves ten steps. Internal route points move with selected groups. Movement is undoable.
- Rotation keeps the current selection, so pressing R repeatedly rotates through each orientation.

- Drag a component from Toolbox onto the canvas; double-click also adds one.
- Click a blue connection port, then another port to create piping, or drag from one port to another. A dashed preview shows the pending connection; Escape cancels. Ports have a screen-sized click tolerance even when zoomed out, and overlapping item bounds do not intercept port clicks.
- New connections are validated before changing the drawing or undo history. The created line is selected automatically so its label and kind can be edited immediately in Details of Selection.
- Select a component to edit tag, description or rotation in Details.
- Select a line to change its label or kind (`process` / `signal`).
- Drag components to move them; connected pipes follow. R rotates selected components.
- Wheel zooms; middle-button drag pans; F fits the drawing.
- Ctrl+D duplicates components and connections between selected components.
- Delete removes selected objects and attached connections. Ctrl+Z / Ctrl+Y undo/redo.
- File > Save writes readable `.pid` JSON. File > Export SVG writes a vector drawing.
- File > Export draw.io creates individual components, editable labels/notes and attached pipe edges. Component artwork is embedded SVG; it is movable/resizable, but its internal strokes are not native draw.io stencil primitives. Metadata is carried on the exported items. This is a one-way export: draw.io edits are not imported back into `.pid`.
- Edit > Add drawing note inserts movable text. Double-click a note to edit it, or change text/width in Details. Notes support copy/paste, duplicate, delete, undo and exports.
- File > Recent drawings reopens saved files. File > Print opens the system print dialog; actual printer output depends on the installed driver and paper configuration.
- View > Example system loads a small editable transfer system.

## Current scope

The built-in library contains **141 component types** across process equipment, vessels/reactors, pumps/compressors, heat transfer, separation/treatment, valves, fittings, pressure protection, steam systems and instrumentation. **Browse components** above Toolbox (or View > Component catalog) provides a searchable large preview, named ports and Insert button. Search by words or tag prefix, such as `gate valve`, `flow`, `PT` or `heat transfer`. See [COMPONENTS.md](COMPONENTS.md) for the complete inventory and coverage limits. Edit > Drawing component library adds reusable custom vector definitions, embedded with the drawing and importable/exportable as `.pidsymbol` files. Rendering, named ports, routing, clipboard and authoring context use the same definitions. See [SYMBOLS.md](SYMBOLS.md). Original artwork is illustrative, not certified standards conformance. Existing file identifiers remain compatible; new types require this updated app.

Arrange aligns selected components horizontally/vertically and distributes three or more selected items. Snap can be toggled and its spacing changed from Arrange. These operations are undoable; snap applies to placement, dragging and route waypoints.

Pipes use obstacle-aware orthogonal routing and honor rotated port directions. Double-click a pipe to add a waypoint; select the pipe to expose draggable waypoint handles. Right-click a handle to remove it, or right-click a pipe to reset automatic routing. Red piping indicates a blocked route, with details in Validate. Each component has a rotated rectangular body/actuator envelope shared through the catalog. These envelopes exclude nozzle leads and tag text; label avoidance and exact-shape clearance are not implemented. Geometry-only caching avoids recomputing unchanged routes during selection and exports.

Ctrl+C / Ctrl+V copy and paste selected components and their internal connections, with new unique IDs and tags. Recovery snapshots are written every 30 seconds while a drawing has unsaved changes. File > Recover autosaved drawing opens retained snapshots after a crash. Clean close removes only the current process's snapshot. Panel layout and window geometry persist between sessions.

File > Drawing settings edits the drawing number, revision, project, author/checker, date and general notes. Edit > Engineering properties edits selected component or piping metadata. File > Export PDF sheet / Export PNG sheet generates a landscape drawing at the selected paper size, with a border and title block. Reports exports component, valve, instrument and line registers as CSV. Metadata is preserved when saving, copying and duplicating.

Drawing settings also selects landscape A4, A3, ANSI B or ANSI D paper; PDF and printing use that physical page size and PNG uses the matching aspect ratio. Validate lists structural errors, blocked routes, unconnected ports, repeated line numbers and duplicate connections. Unused ports and repeated segment numbers are review items because they may be intentional. Click a message to locate the associated object.

Sheet title and general-note cells expand to fit their content. If metadata leaves too little drawing space, preview/export reports an error before overwriting an export; shorten the sheet metadata or move notes onto the drawing. PDF, PNG and preview share device-independent typography. Printing uses the same renderer but remains untested on a physical printer.

Sketch / AI > Attach reference sketch embeds a local image into the drawing for tracing. Reference placement controls its size, position and opacity; the toggle hides it without removing it. The reference is retained across save/open but omitted from exported engineering sheets.

Sketch / AI > Export authoring context writes the actual catalog, schemas, instructions, current document and its fingerprint. Review edit proposal validates operation-based JSON, shows a rendered draft and change list, and applies accepted changes as one undoable transaction. Older proposals are rejected. Generate with OpenAI adds optional text/photo input using a personal API key; see ai/OPENAI_SETUP.md. Live recognition accuracy has not yet been verified.

There is no fluid calculation. Explicit tees express branching; crossings alone do not connect. Full package acceptance and outstanding work are tracked in ROADMAP.md.

## AI integration foundation

`pidcore.py` exposes the shared catalog, validation and atomic saving. `document.schema.json` specifies the format. `ai/AUTHORING.md` defines the authoring contract. `openai_bridge.py` adapts strict API results into local transactions, while `assistant_ui.py` manages asynchronous requests. The offline editor needs no API key.

Typed edit operations, revisions, schema/catalog context, draft review, source-region checks and optional image input are implemented. API usage is separately billed and optional. Remaining package acceptance gates and human-only verification are tracked in [CRITICAL_FEATURES.md](CRITICAL_FEATURES.md).

## Development

Python 3.14 and PySide6 6.11.2 were used for this build.
Install requirements in a virtual environment, then run `python app.py`.
Run `python -m unittest discover` for the full offline regression suite (including actual Qt viewport events and mocked API transport). Synthetic sketch examples and expected review cases are in `examples/sketch-corpus`; these test the pipeline, not model recognition accuracy.
