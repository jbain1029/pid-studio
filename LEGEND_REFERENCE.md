# Drawing reference: pid-legend.pdf

Built-in components with a `legend_reference` field use artwork matched to the
user-supplied **Standard P&ID Symbols Legend**, the single-page Edrawsoft chart
named `pid-legend.pdf`. The original PDF is not bundled or modified. Hover over
a matching component in the editor to see its selected reference entry.

This is a project drawing convention, not a claim of ISA, ISO or other standards
certification. The chart presents several alternatives for some functions.
One appropriate variant is selected per component. Small attachment leads are
adapted to preserve existing saved drawings' named ports and port coordinates.
Composite or adapted matches are identified in their reference descriptions.
Components without a reference field are not claimed to match this chart;
separate engineering and readability corrections may still affect them.
Specialized services cannot safely be inferred from
a generic symbol merely because their silhouettes are similar.

Current coverage: **81 of 141 components** (30 process-equipment, 30 valve/piping,
and 21 instrumentation entries). The other 61 have no selected chart-match claim.
Unmatched examples include specialized regulators/relief configurations,
steam-trap mechanisms, rotary-lobe and metering pumps, membrane modules, and
instrument functions not explicitly shown. Open/floating tank vent leads use an
explicit rim-contact adaptation while retaining the saved attachment and service;
this is not claimed as an exact chart match.

The overlays are maintained in `legend_instruments.py`, `legend_process.py`, and
`legend_valves.py`. They are shared by the editor, component preview, and vector,
image, PDF and draw.io exports. Component IDs, tags, connection endpoints, and
custom `.pidsymbol` files keep their existing format. Built-in reference lettering
and solid fills do not expand the custom-file schema or permit executable content.

Generic instrument bubbles show their declared functional letters and instance
identity. Only the explicitly named legacy Panel controller retains a location
bar; PT/LT and other controllers no longer infer location from the chart's sample.
Simple function-number tags are compacted; compound and arbitrary tags are retained
in full. Long text is fitted and may require a larger drawing scale for readability.
Text remains upright when a component is rotated.
External tags remain available, including as editable labels in draw.io. In a
draw.io export the lettering inside the SVG is a snapshot: re-export from PID
Studio after changing tags to keep internal lettering synchronized.

Orifice and Venturi pressure taps are retained even though the small reference
symbols omit them. Venturi low-pressure attachment reaches the throat. No fluid
calculation or design certification is performed.

The earlier `SYMBOL_AUDIT.md` describes the pre-reference artwork. For current
coverage, inspect each built-in definition's `legend_reference` field; its old
counts must not be treated as a current verification report.

See [the full component study](research/SYMBOL_STUDY.md) and its three exhaustive
appendices for supported families, mismatches, project-specific representations,
unresolved cases and correction records. Matching this reference does not resolve
every engineering-semantic finding or establish standards conformity.

Other inspected primary sources are recorded separately as `symbol_reference`.
The tooltip and drawing-specific component legend identify these as source
conventions, not matches to the supplied chart. They do not inflate the 81-entry
chart count. The component legend fingerprints both drawing data and the used
component definitions so that later library changes can be distinguished.
