import copy
import json
import unittest
from unittest.mock import patch
from test_editor import APP
from app import Window
import pidcore as core
import operations
import openai_bridge as bridge
from assistant_ui import AssistantDialog

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.document = core.new_document()
        self.document['components'].append(core.component('pump',0,0,self.document))
        self.document['components'][0]['metadata'] = {'service':'Water'}
        self.value = {'components':[],'connections':[],'removed_component_ids':[],'removed_connection_ids':[],'title':None,'issues':[], 'review_findings':[]}

    def response(self):
        return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(self.value)}]}]}

    def test_strict_schema_all_object_fields_required(self):
        def inspect(node):
            if isinstance(node,dict):
                if node.get('type')=='object':
                    self.assertFalse(node['additionalProperties'])
                    self.assertEqual(set(node['required']),set(node['properties']))
                for value in node.values():
                    inspect(value)
            elif isinstance(node,list):
                for value in node:
                    inspect(value)
        inspect(bridge.wire_schema())

    def test_request_image_separate_from_document(self):
        self.document['reference'] = {'data':'PRIVATE_BYTES','filename':'sketch.png','width':1000,'position':[0,0],'opacity':.4}
        body = bridge.request_body(self.document,'Transcribe sketch','test-model','data:image/png;base64,abc')
        self.assertFalse(body['store'])
        self.assertEqual(body['text']['format']['strict'],True)
        self.assertNotIn('PRIVATE_BYTES',json.dumps(body))
        self.assertEqual(body['input'][0]['content'][1]['type'],'input_image')
        self.assertIn('catalog',body['input'][0]['content'][0]['text'])

    def test_upsert_preserves_metadata_and_validates(self):
        record = copy.deepcopy(self.document['components'][0])
        record.pop('metadata')
        record['position'] = {'x':200,'y':100}
        record['tag'] = 'P-201'
        self.value['components'] = [record]
        proposal = bridge.decode_response(self.document,self.response())
        result = operations.apply(self.document,proposal)
        self.assertEqual(result['components'][0]['metadata'],{'service':'Water'})
        self.assertEqual(result['components'][0]['position'],[200,100])
        self.assertEqual(self.document['components'][0]['tag'],'P-101')

    def test_refusal_incomplete_bad_json_invalid_endpoint(self):
        responses = [{'status':'incomplete'}, {'status':'completed','output':[{'content':[{'type':'refusal'}]}]},
            {'status':'completed','output':[{'content':[{'type':'output_text','text':'not json'}]}]}]
        for response in responses:
            with self.assertRaises(ValueError):
                bridge.decode_response(self.document,response)
        self.value['connections'] = [{'id':'bad','from':{'component':'missing','port':'outlet'},'to':{'component':'missing','port':'inlet'},'kind':'process','label':'','waypoints':[]}]
        with self.assertRaises(ValueError):
            bridge.decode_response(self.document,self.response())

    def test_dialog_does_not_request_on_open(self):
        window = Window()
        with patch('keyring.get_password',return_value=None), patch.dict('os.environ',{'OPENAI_API_KEY':'','OPENAI_MODEL':''}):
            dialog = AssistantDialog(window)
            dialog.key.clear()
            dialog.model.clear()
            with patch.object(dialog.manager,'post') as send:
                dialog.start()
                send.assert_not_called()
            self.assertIsNone(dialog.reply)
            self.assertIn('Enter a model',dialog.status.text())
            dialog.reject()
        window.close()

    def test_findings_pass_through_and_invalid_regions_fail_atomically(self):
        self.document['reference'] = {'data':'fixture','filename':'sketch.png','width':1000,'position':[0,0],'opacity':.4}
        finding = {'id':'f1','message':'Confirm pump tag','region':{'x':.1,'y':.2,'width':.3,'height':.4},
                   'object_ids':[self.document['components'][0]['id']]}
        self.value['review_findings'] = [finding]
        original = copy.deepcopy(self.document)
        proposal = bridge.decode_response(self.document,self.response(),image_included=True)
        self.assertEqual(proposal['review_findings'],[finding])
        with self.assertRaisesRegex(ValueError,'no image was sent'):
            bridge.decode_response(self.document,self.response())
        finding['region']['width'] = 1
        with self.assertRaisesRegex(ValueError,'within the source image'):
            bridge.decode_response(self.document,self.response(),image_included=True)
        self.assertEqual(self.document,original)

    def test_text_only_request_and_general_finding(self):
        self.document['reference'] = {'data':'PRIVATE_BYTES','filename':'sketch.png','width':1000,'position':[0,0],'opacity':.4}
        body = bridge.request_body(self.document,'Check tags','test-model')
        data = json.loads(body['input'][0]['content'][0]['text'])
        self.assertFalse(data['image_included'])
        self.assertIsNone(data['image_placement'])
        self.assertEqual(body['text']['format']['name'],'pid_changes_v2')
        self.value['review_findings'] = [{'id':'f1','message':'Confirm service','region':None,'object_ids':[]}]
        proposal = bridge.decode_response(self.document,self.response())
        self.assertEqual(proposal['review_findings'],self.value['review_findings'])

    def test_missing_required_findings_is_rejected(self):
        self.value.pop('review_findings')
        with self.assertRaisesRegex(ValueError,'schema'):
            bridge.decode_response(self.document,self.response())

if __name__=='__main__':
    unittest.main()
