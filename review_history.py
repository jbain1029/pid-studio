"""Local acceptance records, persisted with the drawing and undone with edits."""
import base64
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QDialogButtonBox
from PySide6.QtCore import Qt
import pidcore as core
import operations


def append(draft, before, proposal, *, generation=None):
    """Return a new draft containing the record; never mutate the input objects."""
    root = Path(__file__).parent
    reference = before.get('reference')
    source_hash = None
    if reference:
        try:
            source_hash = hashlib.sha256(base64.b64decode(reference['data'],validate=True)).hexdigest()
        except (ValueError,TypeError):
            # A non-image proposal can be accepted despite an unreadable attachment.
            pass
    record = {
        'id':core.uid(), 'accepted_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'base_fingerprint':operations.fingerprint(before),
        'proposal_fingerprint':operations.fingerprint(proposal),
        'source_fingerprint':source_hash,
        'catalog_fingerprint':operations.fingerprint(core.catalog_for(before)),
        'schema_fingerprint':hashlib.sha256((root/'document.schema.json').read_bytes()).hexdigest(),
        'authoring_fingerprint':hashlib.sha256((root/'ai'/'AUTHORING.md').read_bytes()).hexdigest(),
        'proposal_json':json.dumps(proposal,sort_keys=True,separators=(',',':'),allow_nan=False),
        'acknowledged_ids':[f['id'] for f in proposal.get('review_findings',[])],
    }
    if generation is not None:
        import generation_provenance
        generation_provenance.validate(generation,record['base_fingerprint'])
        record['generation'] = copy.deepcopy(generation)
    result = copy.deepcopy(draft)
    result.setdefault('review_history',[]).append(record)
    errors = core.validate(result)
    if errors:
        raise ValueError('\n'.join(errors))
    return result


class HistoryDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self.setWindowTitle('Accepted proposal history')
        self.resize(850,570)
        layout = QVBoxLayout(self)
        label = QLabel('Local review records travel with this drawing. They record acknowledgment, not engineering approval.\nFingerprints help identify content; this editable file is not a signed or tamper-proof audit log.')
        label.setWordWrap(True)
        layout.addWidget(label)
        self.tree = QTreeWidget()
        self.tree.setRootIsDecorated(False)
        self.tree.setHeaderLabels(['Accepted (UTC)', 'Review checks', 'Record ID'])
        self.tree.setColumnWidth(0,240)
        self.tree.setColumnWidth(1,130)
        self.tree.setMaximumHeight(180)
        layout.addWidget(self.tree)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        layout.addWidget(self.details,1)
        self.tree.currentItemChanged.connect(self.inspect)
        for record in reversed(window.document.get('review_history',[])):
            item = QTreeWidgetItem(self.tree,[record['accepted_at'],str(len(record['acknowledged_ids'])),record['id']])
            item.setData(0,Qt.ItemDataRole.UserRole,record)
        if self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))
        else:
            self.details.setPlainText('No accepted proposal records in this drawing. Older drawings may predate review-history recording.')
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def inspect(self, item, previous=None):
        if item is None:
            return
        record = item.data(0,Qt.ItemDataRole.UserRole)
        try:
            proposal = json.loads(record['proposal_json'])
            matches = operations.fingerprint(proposal) == record['proposal_fingerprint']
            content = json.dumps(proposal,indent=2,ensure_ascii=False)
        except (ValueError,TypeError):
            matches, content = False, record['proposal_json']
        header = [f"Accepted: {record['accepted_at']}",f"Proposal fingerprint matches stored content: {'yes' if matches else 'NO'}",
                  f"Attached image SHA-256 (not proof of upload): {record['source_fingerprint'] or 'unavailable / no attachment'}",
                  f"Catalog: {record['catalog_fingerprint']}",f"Schema: {record['schema_fingerprint']}",
                  f"Authoring instructions: {record['authoring_fingerprint']}",
                  'Acknowledged checks: '+', '.join(record['acknowledged_ids'])]
        import generation_provenance
        self.details.setPlainText('\n'.join(header)+'\n\n'+generation_provenance.describe(record.get('generation'))+'\n\nACCEPTED PROPOSAL\n'+content)


def show(window):
    HistoryDialog(window).exec()
