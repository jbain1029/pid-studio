"""Optional asynchronous OpenAI input dialog. No network calls until Generate."""
import base64
import copy
import json
import os
from PySide6.QtCore import Qt, QUrl, QTimer, QBuffer, QIODevice
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QLineEdit,QPlainTextEdit,QCheckBox,
    QPushButton,QHBoxLayout,QLabel,QMessageBox,QProgressBar)
import openai_bridge
import sketch
import generation_provenance

class AssistantDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.reply = None
        self.setWindowTitle('AI Drafting Assistant — OpenAI')
        self.resize(640,520)
        layout = QVBoxLayout(self)
        notice = QLabel('Generate a draft from instructions and, optionally, the attached sketch.\nGenerate sends the current drawing and selected image to OpenAI. API usage is separately billed.')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        provenance_notice = QLabel('Accepted drafts save model/response identifiers, token counts and content fingerprints in the drawing.\nAPI keys, request text and submitted image payloads are not copied into those records.')
        provenance_notice.setWordWrap(True)
        layout.addWidget(provenance_notice)
        form = QFormLayout()
        layout.addLayout(form)
        self.model = QLineEdit(window.workbench_settings.value('openai_model',os.getenv('OPENAI_MODEL','')))
        self.model.setPlaceholderText('Your image-capable model ID')
        form.addRow('Model',self.model)
        self.key = QLineEdit()
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        self.key.setPlaceholderText('API key — kept in memory unless Remember is checked')
        saved_key = ''
        try:
            import keyring
            saved_key = keyring.get_password('PIDStudio','OpenAI') or ''
        except Exception:
            pass
        self.key.setText(saved_key or os.getenv('OPENAI_API_KEY',''))
        form.addRow('API key',self.key)
        self.remember = QCheckBox('Remember key in operating-system credential storage')
        layout.addWidget(self.remember)
        forget = QPushButton('Forget saved key')
        forget.clicked.connect(self.forget_key)
        form.addRow('',forget)
        self.use_image = QCheckBox('Include attached reference sketch')
        self.use_image.setEnabled('reference' in window.document)
        self.use_image.setChecked('reference' in window.document)
        layout.addWidget(self.use_image)
        self.instructions = QPlainTextEdit()
        self.instructions.setPlaceholderText('Describe the system or the changes to make. Attach a sketch from the Sketch / AI menu first if needed.')
        layout.addWidget(self.instructions,1)
        self.status = QLabel('Ready. Generated changes will open in a review window.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0,0)
        self.progress.hide()
        layout.addWidget(self.progress)
        buttons = QHBoxLayout()
        self.generate = QPushButton('Generate draft')
        self.generate.clicked.connect(self.start)
        self.cancel = QPushButton('Close')
        self.cancel.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(self.generate)
        buttons.addWidget(self.cancel)
        layout.addLayout(buttons)
        self.manager = QNetworkAccessManager(self)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)

    def forget_key(self):
        try:
            import keyring
            if keyring.get_password('PIDStudio','OpenAI'):
                keyring.delete_password('PIDStudio','OpenAI')
            self.key.clear()
            self.status.setText('Saved key removed.')
        except Exception:
            self.status.setText('Credential storage is unavailable. No key was changed.')

    def start(self):
        if self.reply is not None:
            return
        if not self.model.text().strip() or not self.key.text().strip() or not self.instructions.toPlainText().strip():
            self.status.setText('Enter a model ID, API key and drafting instructions.')
            return
        if self.remember.isChecked():
            try:
                import keyring
                keyring.set_password('PIDStudio','OpenAI',self.key.text().strip())
            except Exception:
                self.status.setText('Could not store the key securely. Uncheck Remember to use it for this request.')
                return
        self.window.workbench_settings.setValue('openai_model',self.model.text().strip())
        self.snapshot = copy.deepcopy(self.window.document)
        image_url = None
        if self.use_image.isChecked():
            image = self.window.reference_image
            if image.isNull():
                self.status.setText('The attached sketch could not be decoded. Attach a readable image.')
                return
            # Normalize to a supported format and bound payload size; original stays in .pid.
            image = image.scaled(2400,2400,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            image.save(buffer,'PNG')
            image_url = 'data:image/png;base64,'+base64.b64encode(bytes(buffer.data())).decode()
        body = openai_bridge.request_body(self.snapshot,self.instructions.toPlainText(),self.model.text().strip(),image_url)
        self.image_included = image_url is not None
        if len(json.dumps(body['input'][0]['content'][0]))>500000:
            self.status.setText('This drawing exceeds the AI input limit. Work on a smaller sheet.')
            return
        request = QNetworkRequest(QUrl('https://api.openai.com/v1/responses'))
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader,'application/json')
        request.setRawHeader(b'Authorization',('Bearer '+self.key.text().strip()).encode())
        self.cancelled = False
        payload = json.dumps(body).encode()
        self.generation = generation_provenance.capture(self.snapshot,body,payload)
        self.reply = self.manager.post(request,payload)
        self.reply.finished.connect(self.request_finished)
        self.reply.downloadProgress.connect(self.check_size)
        self.timer.start(180000)
        self.generate.setEnabled(False)
        self.progress.show()
        self.cancel.setText('Cancel request')
        self.status.setText('Generating draft… You can cancel; the current drawing remains available after this dialog closes.')

    def check_size(self, received, total):
        if received>8_000_000 and self.reply:
            self.cancelled = True
            self.reply.abort()
            self.status.setText('Response exceeded the size limit. No changes applied.')

    def timeout(self):
        if self.reply:
            self.cancelled = True
            self.reply.abort()
            self.status.setText('Request timed out. No changes applied; a submitted request may still incur API charges.')

    def request_finished(self):
        reply, self.reply = self.reply, None
        if reply is None:
            return
        self.timer.stop()
        self.generate.setEnabled(True)
        self.progress.hide()
        self.cancel.setText('Close')
        try:
            if self.cancelled:
                return
            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if status and 300 <= status < 400:
                self.status.setText('Unexpected API redirect rejected. No changes applied.')
                return
            if reply.error() != QNetworkReply.NetworkError.NoError:
                messages = {401:'API key rejected.',403:'This project cannot access the requested model.',429:'Rate or account usage limit reached.'}
                self.status.setText(messages.get(status,f'API request failed (HTTP {status or "unavailable"}). Check your network, model ID and account settings.'))
                return
            response = json.loads(bytes(reply.readAll()))
            proposal = openai_bridge.decode_response(self.snapshot,response,image_included=self.image_included)
            generation = generation_provenance.finish(self.generation,response)
            used = generation['total_tokens']
            accepted = sketch.review(self.window,proposal,generation=generation)
            self.status.setText(('Draft applied.' if accepted else 'Draft discarded.')+(f' API usage: {used} tokens.' if used else ''))
        except (ValueError,KeyError,TypeError) as error:
            self.status.setText(str(error))
        finally:
            reply.deleteLater()

    def reject(self):
        if self.reply:
            self.cancelled = True
            self.reply.abort()
        super().reject()

def install(window):
    menu = next(a.menu() for a in window.menuBar().actions() if a.text()=='Sketch / AI')
    menu.addSeparator()
    action = menu.addAction('Generate with OpenAI…')
    action.triggered.connect(lambda:AssistantDialog(window).exec())
