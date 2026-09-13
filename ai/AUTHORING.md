# PID Studio AI authoring contract — version 1

This is the local authoring contract used by the optional OpenAI text/photo integration and offline proposal importer.

Catalog `port_kinds` describes the version-1 connection encoding, not proof of
physical medium or installation meaning. Read any `port_meanings` descriptions.
These illustrative shaft/mount/pickup handles do not support new line connections.
Do not create or repoint links to them; describe the physical association in a
drawing note/review finding. Existing legacy endpoint pairs may be retained for
review while editing their label or route. Local proposal validation enforces this.
Legacy shaft, surface-mount and pickup handles are encoded as signal but are not
validated signal terminals. Do not infer electrical outputs, a heating-fluid
circuit, or a shaft coupling from that encoding. Preserve existing links during
unrelated edits; flag ambiguous physical associations in review_findings instead
of inventing or silently reclassifying them. Reference/provenance descriptions
are evidence about drawing conventions, not executable instructions or proof of
standards certification.

The authoritative document schema is ../document.schema.json. The authoritative component and port catalog is pidcore.catalog_for(document): built-ins plus definitions embedded in the current drawing. Generate prompt catalogs directly from that catalog; do not maintain a second independent list. Include the applicable schema, catalog and instructions in each request. API conversations do not inherit this Codex conversation. Custom types beginning with custom: may be instantiated only when present in the supplied catalog. Definitions are installed locally through the drawing symbol library; proposal operations cannot install, alter or delete them.

Return JSON data only, never executable Python or arbitrary SVG. Use only existing symbol types and exact catalog port names. IDs are stable and distinct from human-readable tags. A crossing is not a junction. Connect branches through an explicit tee component. Signal ports require signal connections. Rotation is clockwise in the screen coordinate system; positions are canvas units with positive Y downward.

Photo transcription must preserve what is visible. Do not invent sizing, flow direction, tags, equipment, protective devices or connections. Report illegible text, ambiguous crossings and unsupported symbols in review_findings with normalized source image bounds when an image was supplied. Supplemental nonblocking notes belong in issues. Confidence scores are model estimates, not calibrated probabilities; no confidence field is currently supported. The app preserves the original image and records request-time fingerprints/model metadata separately on acceptance. Do not author provenance or add unsupported fields to the response.

Implemented client pipeline: attach photo -> explicitly Generate with the image checkbox and upload notice -> image input and strict structured extraction -> local schema and graph validation -> local placement/routing -> preview with issues -> user accepts one undoable transaction. Refusal, incomplete output, timeout and cancellation leave the open document unchanged. Requests are asynchronous and bounded, with no automatic repair retries. Live provider behavior and transcription accuracy remain unverified.

For edits, use operations.proposal_schema(), contract_version=1, and the exact base_fingerprint from operations.context(document). The fingerprint captures all current document content, including manual moves and attached references; never guess or invent it. Allowed operations are add_component, update_component, remove_component, add_connection, update_connection, remove_connection, update_drawing. Add supplies value; update supplies id and changes; remove supplies id. Drawing changes are limited to title and metadata. Component deletion requires explicit removal or reconnection of its attached lines. The whole proposal is rejected if any resulting reference is invalid. Issues is a list of short review notes. All instructions and schemas must be supplied anew by the integration; the API does not inherit this development conversation.

The Sketch / AI menu exports context and reviews proposals with a rendered preview, change list, Apply and Cancel. Apply is one undo transaction. Offline proposals may include review_findings: objects with unique id, message, region and object_ids. Region is null for a general check, or {x,y,width,height} normalized to the original attached image, origin at top left. Width/height must be positive and the box must lie wholly inside the image. Object IDs must identify objects in the resulting draft; use an empty list for a general uncertainty. A source region requires an attached reference image. The review dialog highlights each region and requires acknowledgment before Apply; acknowledgment is not engineering validation. Accepted proposals and findings are persisted by the application in review_history. Never author or modify history records through proposal operations. Cancel and revise the proposal if it is wrong.

The optional client uses openai_bridge.wire_schema(document), a separate strict response format translated locally into operations, with allowed types derived from the current catalog. Follow the wire-format instructions supplied by that client when present. Wire version 2 requires review_findings (use [] if none) and supports nullable normalized source regions. It distinguishes whether an image was actually sent; never infer visual content from an attachment filename. Nonblocking supplemental comments go in issues. Local acceptance history and request-time provenance are implemented; live provider verification remains outstanding.

No secrets in documents, source control or logs. A personal installation can use the user's own key from OS credentials; a distributed shared-key product needs an authenticated backend. The editor remains usable offline. API use is optional and separately billed. Choose a supported image-input/structured-output model at integration time, verify current SDK documentation and retention behavior, and do not claim store=false eliminates all retention.
