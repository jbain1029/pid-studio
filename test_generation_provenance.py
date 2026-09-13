"""Offline request provenance tests: no credentials, network, or provider access."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import generation_provenance as provenance
import openai_bridge as bridge
import operations
import pidcore as core
import review_history


class GenerationProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.document = core.new_document()
        self.document['title'] = 'Réservoir — 水'
        self.document['reference'] = {
            'filename': 'original.png',
            'data': base64.b64encode(b'original attachment bytes').decode('ascii'),
            'position': [0, 0], 'width': 1000, 'opacity': .4,
        }
        self.instruction = 'Rename the pump café — 水, keep the valve.'

    def captured(self, image=None):
        body = bridge.request_body(self.document, self.instruction, 'offline-test-model', image)
        payload = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        return provenance.capture(self.document, body, payload), body, payload

    def proposal(self, document=None):
        document = self.document if document is None else document
        return {'contract_version': 1, 'base_fingerprint': operations.fingerprint(document),
                'operations': [{'operation': 'update_drawing', 'changes': {'title': 'Accepted title'}}]}

    def test_capture_fingerprints_exact_unicode_payload_and_request_inputs(self):
        original = copy.deepcopy(self.document)
        record, body, payload = self.captured()
        self.assertIn('水'.encode('utf-8'), payload)
        self.assertEqual(record['request_fingerprint'], hashlib.sha256(payload).hexdigest())
        reformatted = json.dumps(body, ensure_ascii=False, indent=2).encode('utf-8')
        self.assertNotEqual(record['request_fingerprint'], hashlib.sha256(reformatted).hexdigest())
        self.assertEqual(record['user_instruction_fingerprint'], hashlib.sha256(self.instruction.encode('utf-8')).hexdigest())
        self.assertEqual(record['instructions_fingerprint'], hashlib.sha256(body['instructions'].encode('utf-8')).hexdigest())
        self.assertEqual(record['wire_schema_fingerprint'], operations.fingerprint(body['text']['format']['schema']))
        self.assertEqual(record['catalog_fingerprint'], operations.fingerprint(core.CATALOG))
        self.assertEqual(record['document_schema_fingerprint'], hashlib.sha256(Path(core.__file__).with_name('document.schema.json').read_bytes()).hexdigest())
        self.assertEqual(record['base_fingerprint'], operations.fingerprint(original))
        provenance.validate(record, operations.fingerprint(original))
        self.assertEqual(self.document, original)

    def test_sent_image_fingerprint_is_exact_payload_image_not_attachment(self):
        sent_bytes = b'prepared PNG fixture; intentionally different from attachment'
        image = 'data:image/png;base64,' + base64.b64encode(sent_bytes).decode('ascii')
        record, _, _ = self.captured(image)
        self.assertTrue(record['image_included'])
        self.assertEqual(record['sent_image_fingerprint'], hashlib.sha256(sent_bytes).hexdigest())
        self.assertNotEqual(record['sent_image_fingerprint'], hashlib.sha256(base64.b64decode(self.document['reference']['data'])).hexdigest())
        provenance.validate(record, operations.fingerprint(self.document))

    def test_attached_image_is_not_claimed_as_sent_for_text_only_request(self):
        record, _, _ = self.captured()
        self.assertFalse(record['image_included'])
        self.assertIsNone(record['sent_image_fingerprint'])
        self.assertIsNone(record['received_at'])
        self.assertIsNone(record['response_id'])
        self.assertIn('payload: no', provenance.describe(record))

    def test_finish_copies_only_allowlisted_response_fields_and_does_not_mutate(self):
        captured, _, _ = self.captured()
        original = copy.deepcopy(captured)
        response = {'id': 'response-fixture', 'model': 'returned-model',
                    'usage': {'input_tokens': 12, 'output_tokens': 3, 'total_tokens': 15,
                              'private_details': 'never retained'},
                    'output': [{'text': 'not stored here'}], 'headers': {'Authorization': 'fake-secret'}}
        response_before = copy.deepcopy(response)
        finished = provenance.finish(captured, response)
        self.assertEqual(captured, original)
        self.assertEqual(response, response_before)
        self.assertEqual(set(finished), set(captured))
        self.assertEqual(finished['response_id'], 'response-fixture')
        self.assertEqual(finished['response_model'], 'returned-model')
        self.assertEqual([finished[key] for key in ('input_tokens', 'output_tokens', 'total_tokens')], [12, 3, 15])
        self.assertTrue(finished['received_at'])
        self.assertNotIn('fake-secret', json.dumps(finished))
        self.assertNotIn('never retained', json.dumps(finished))
        finished['requested_model'] = 'changed'
        self.assertEqual(captured, original)

    def test_finish_missing_null_and_malformed_metadata_stays_unknown(self):
        captured, _, _ = self.captured()
        for value in (None, True, False, -1, 1.5, '12', {}, [], ''):
            with self.subTest(usage_value=value):
                result = provenance.finish(captured, {'usage': dict.fromkeys(('input_tokens', 'output_tokens', 'total_tokens'), value)})
                for key in ('input_tokens', 'output_tokens', 'total_tokens'):
                    self.assertIsNone(result[key])
        for value in (None, {}, [], 12, True, '', 'x' * 257):
            with self.subTest(identity_value=value):
                result = provenance.finish(captured, {'id': value, 'model': value})
                self.assertIsNone(result['response_id'])
                self.assertIsNone(result['response_model'])
        for value in (None, [], 'usage', 12):
            with self.subTest(usage_container=value):
                result = provenance.finish(captured, {'usage': value})
                self.assertIsNone(result['total_tokens'])
        result = provenance.finish(captured, {'usage': {'input_tokens': 0}, 'id': 'x' * 256})
        self.assertEqual(result['input_tokens'], 0)
        self.assertEqual(result['response_id'], 'x' * 256)

    def test_validation_rejects_wrong_base_image_inconsistency_and_unknown_keys(self):
        record, _, _ = self.captured()
        with self.assertRaisesRegex(ValueError, 'different drawing state'):
            provenance.validate(record, '0' * 64)
        for changes in ({'image_included': True}, {'sent_image_fingerprint': 'a' * 64},
                        {'request_fingerprint': 'not-a-hash'}, {'secret': 'not allowed'}):
            with self.subTest(changes=changes):
                bad = dict(record, **changes)
                with self.assertRaises(ValueError):
                    provenance.validate(bad, operations.fingerprint(self.document))

    def test_capture_rejects_wrong_image_format_bad_base64_and_multiple_images(self):
        for image in ('data:image/jpeg;base64,YWJj', 'data:image/png;base64,***'):
            with self.subTest(image=image), self.assertRaises(ValueError):
                self.captured(image)
        _, body, _ = self.captured('data:image/png;base64,YWJj')
        body['input'][0]['content'].append(copy.deepcopy(body['input'][0]['content'][1]))
        with self.assertRaisesRegex(ValueError, 'Only one'):
            provenance.capture(self.document, body, json.dumps(body).encode())

    def test_acceptance_roundtrip_keeps_generation_independent_of_original_inputs(self):
        captured, _, _ = self.captured('data:image/png;base64,YWJj')
        generation = provenance.finish(captured, {'id': 'response-fixture', 'model': 'returned-model'})
        proposal = self.proposal()
        draft = operations.apply(self.document, proposal)
        originals = copy.deepcopy((self.document, proposal, draft, generation))
        result = review_history.append(draft, self.document, proposal, generation=generation)
        self.assertEqual((self.document, proposal, draft, generation), originals)
        record = result['review_history'][0]
        self.assertEqual(record['generation'], generation)
        self.assertNotEqual(record['source_fingerprint'], record['generation']['sent_image_fingerprint'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'provenance.pid'
            core.save(result, path)
            self.assertEqual(core.load(path), result)
        generation['response_id'] = 'later mutation'
        self.assertEqual(record['generation']['response_id'], 'response-fixture')
        self.assertNotIn('review_history', self.document)

    def test_invalid_generation_cannot_create_acceptance_record(self):
        generation, _, _ = self.captured()
        generation['base_fingerprint'] = 'a' * 64
        proposal = self.proposal()
        draft = operations.apply(self.document, proposal)
        before = copy.deepcopy((draft, self.document))
        with self.assertRaises(ValueError):
            review_history.append(draft, self.document, proposal, generation=generation)
        self.assertEqual((draft, self.document), before)

    def test_request_omits_local_history_without_changing_full_snapshot_fingerprint(self):
        proposal = self.proposal()
        self.document = review_history.append(operations.apply(self.document, proposal), self.document, proposal)
        before = copy.deepcopy(self.document)
        record, body, _ = self.captured()
        supplied = json.loads(body['input'][0]['content'][0]['text'])['current_document']
        self.assertNotIn('review_history', supplied)
        self.assertNotIn('reference', supplied)
        self.assertEqual(supplied['title'], before['title'])
        self.assertEqual(record['base_fingerprint'], operations.fingerprint(before))
        self.assertNotEqual(record['base_fingerprint'], operations.fingerprint(supplied))
        self.assertEqual(self.document, before)

    def test_older_offline_record_description_does_not_claim_generation(self):
        self.assertIn('No request-time provenance', provenance.describe(None))


if __name__ == '__main__':
    unittest.main()
