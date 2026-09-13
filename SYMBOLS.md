# Reusable drawing components

Edit > Drawing component library manages custom components for the current drawing.
New starts with a sight-glass example. Edit its JSON, use Preview, then Apply to
drawing. The component appears in Toolbox and can be dragged or double-clicked onto
the canvas like a built-in component. Save the drawing to keep its library.

The diagram editor remains the normal drag/drop interface; the library editor is
an optional code-friendly definition tool, not a general-purpose CAD modeler.

## Portability and safe changes

- Import/Export reads or writes a `.pidsymbol` JSON file. Import stages a preview;
  Apply adds it to the drawing. A conflicting existing kind is rejected instead
  of overwritten. Select the existing entry to deliberately edit it.
- Definitions are embedded in `.pid` drawings, including unused installed entries.
  No machine-global registry or external image file is needed to reopen them.
- Applying an existing definition updates every instance of that kind, as one
  undoable change. The whole drawing is validated first; removing a connected
  port is rejected. Change pipes first if a port must be removed.
- Remove unused cannot remove a definition that still has instances. Undo restores
  definition additions, edits and removal. Closing the library does not apply
  unapplied JSON text.
- Copy/paste carries only definitions used by the selection. If the destination
  uses the same kind ID for different artwork or ports, the pasted kind receives
  an unused `_2`, `_3`, etc. suffix. Existing components are not changed.

## File format

The `.pidsymbol` extension and internal format identifiers are retained for file
compatibility; the editor calls drawing items components.

The envelope contains `format: "pid-studio-symbol"`, `version: 1`, a `kind` ID,
and `definition`. IDs start with `custom:` followed by a lowercase letter and up
to 47 further lowercase letters, digits or underscores. Built-in IDs cannot be
overridden. See `examples/sight-glass.pidsymbol` for a complete working file.

Definition fields:

| Field | Meaning |
| --- | --- |
| `label`, `prefix`, `category` | Toolbox name, automatic tag prefix, group heading. |
| `ports` | Named positions `[x,y]` in unrotated local coordinates. |
| `port_kinds` | Exactly the same names, each `process` or `signal`. |
| `routing_bounds` | Rectangular body envelope `[left,top,right,bottom]`; exclude nozzle leads. |
| `artwork` | Ordered vector primitives drawn with the app's normal line weight and white fills. |

Allowed artwork primitives are `line`, `polyline`, and `polygon` with `points`,
or `rect` and `ellipse` with `rect: [x,y,width,height]`. Coordinates fit within
`[-45,45]`. Rectangles and ellipses require positive width/height and bounded ends.
The origin is the component center; increasing y points down. Component rotation
rotates artwork, ports and routing bounds together while keeping tags upright.

Ports fit within `[-50,50]`, cannot overlap or sit at the origin, and must be
outside/on the routing body. The automatic outward port stub must remain clear
at all four supported rotations. Bodies should accurately enclose the artwork
that pipes must avoid; the software cannot infer the intended engineering body
from decorative lines. Use short lead lines to join each port to the body.

Definitions are bounded to 16 ports and 64 primitives; a drawing holds up to 64
custom definitions. Imports are limited to 256 KB and bounded JSON nesting.
Scripts, external URLs, raw SVG and arbitrary executable expressions are not
supported. These are illustrative drafting symbols, not certified standard art.

## Reports and AI

All custom components appear in the component register. Set category exactly to
`Instrumentation` or `Valves & Actuators` to include them in those specialized
registers as well. Other category names create ordinary toolbox groups.

Authoring context exports the merged built-in/custom catalog, actual document
schema and definitions. The optional API response schema only permits types
installed in the request's drawing. The AI may place or modify instances of these
types; it cannot install or silently alter definitions through an edit proposal.
The local validator still checks named ports and geometry before acceptance.
