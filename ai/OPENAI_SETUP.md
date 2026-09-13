# Optional OpenAI drafting

Use Sketch / AI > Generate with OpenAI. Enter an API model ID with image input and Structured Outputs support, your personal API key, and instructions. OPENAI_MODEL and OPENAI_API_KEY environment variables are supported. This uses the separately billed OpenAI API, not a ChatGPT subscription.

For photo input, attach a sketch first and check Include attached reference sketch. Generate sends the current drawing, catalog, instructions and selected image to https://api.openai.com/v1/responses. Review the result and listed uncertainties. Apply makes one undoable change; Cancel leaves the drawing unchanged.

The key stays in memory unless Remember is checked. Remember uses the operating-system keyring (Windows Credential Manager). Forget saved key removes that credential. No key is stored in drawings or logs. A distributed shared-key product would require an authenticated backend; the implemented pathway uses the user's own key.

Requests use store=false, which does not guarantee zero provider retention. Images are normalized to PNG at a maximum 2400-pixel side; small text on large sheets may be lost. The original image stays embedded locally. One request is permitted at a time, with a 180-second timeout, no automatic retries, and a 12,000 output-token cap. Cancelling the local reply does not guarantee cancellation of provider computation or charges. Configure account spending limits separately.

openai_bridge.py generates a strict wire schema and translates returned changes into validated operations. Metadata is preserved; stale proposals are rejected using the document fingerprint. Local tests cover schema structure, request payloads, refusals, incomplete output, invalid JSON, invalid endpoints, and metadata preservation.

Wire format v2 requires review_findings, with nullable source regions and affected draft object IDs. The adapter validates normalized bounds and references before review, and rejects image-region claims if no image was sent. The review dialog highlights image regions and requires acknowledgment of each finding before Apply. Supplemental nonblocking notes remain in issues. Acknowledgment is not engineering approval; cancel and revise incorrect interpretations.

Accepted API drafts now retain request-time provenance in the drawing's local review history: requested/returned model IDs, response ID, UTC times, reported token counts, and SHA-256 fingerprints for the exact serialized request body, user/system instructions, wire schema, catalog, local validation schema and actual normalized PNG included in the payload. The original attachment fingerprint remains separate. These editable records identify locally prepared content; they are not signed proof of provider receipt, engineering approval, or a replayable request archive. Request text, API keys and submitted image payloads are not copied into these records. Older/offline proposals show that request-time provenance is unavailable.

Prior review history is excluded from subsequent model inputs to avoid recursive growth and sending previous records unnecessarily. The full local document fingerprint is still used to reject stale responses. Provenance is shown before Apply and saved only with accepted changes; Cancel leaves the drawing and history unchanged.

Live API schema acceptance, real-network cancellation and photo recognition accuracy remain unverified. Mock responses do not establish image recognition quality. A representative evaluation corpus remains follow-up work. Local tests cover the new strict schema, region pass-through, text-only handling and atomic rejection of invalid regions.

Official references checked during implementation:
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://developers.openai.com/api/docs/guides/images-vision
- https://developers.openai.com/api/reference/cli/resources/responses/methods/create
