# Offline sketch fixtures

These three original, synthetic SVG sketches and manually authored expected drafts exercise the local photo-to-proposal pipeline without an API, credentials, or network. They are deliberately simple and are not engineering designs or standards-certified symbols.

| Case | Expected result | Review requirement |
| --- | --- | --- |
| transfer | Tank, pump, isolation valve; two process connections | None in this controlled fixture |
| signal-loop | Panel controller and control valve; one signal connection | None in this controlled fixture |
| ambiguous-crossing | Two identified components; literal unresolved `P-?` pump tag; no inferred connection | Both tag and crossing source regions must be acknowledged |

Run `python -m unittest test_sketch_corpus -v` from the project directory. Tests rasterize the SVGs locally to 3200 × 1600 images, exercise the actual assistant image normalization through a mocked transport, and check the resulting 2400 × 1200 PNG and matching normalized review boxes. The original attachment is retained. The supplied response fixtures pass through the real strict response decoder and document validator, then the real review dialog. Cancel and incomplete review must leave the drawing unchanged; acceptance saves acknowledgments and can be undone.

`cases.json` is test fixture data, **not** an importable proposal or drawing file. A proposal must be constructed against the exact current document fingerprint. The tests do this explicitly. SVG source files are for this test renderer; attach a raster PNG/JPEG when using the application's attachment dialog.

This corpus proves local transformation, validation, and review behavior only. It does **not** prove handwriting recognition, model accuracy, resistance to every prompt injection, provider compatibility, or engineering correctness. Responses are authored by the test, not recognized from the images. Representative user-approved photographs and an explicitly authorized live provider evaluation remain separate work.
