"""Desktop entry point and offline packaged-runtime verification."""
import sys


def smoke_test(folder):
    import os
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    import json
    import copy
    from pathlib import Path
    from PySide6.QtWidgets import QApplication, QTabWidget
    from PySide6.QtGui import QImage, QFontDatabase, QFont, QMouseEvent
    from PySide6.QtPdf import QPdfDocument
    import app
    import classic
    import pidcore
    import operations
    import deliverables
    import drawio_export
    import editing
    import sheet_preview
    import recovery
    import sketch
    import review_history
    import generation_provenance
    import openai_bridge
    import custom_symbols
    import symbol_library
    import connection_editor
    import component_browser
    from source_review import SourceReview
    from PySide6.QtCore import QTimer, Qt, QEvent, QPointF
    from PySide6.QtWidgets import QDialogButtonBox
    output = Path(folder).resolve()
    # Never overwrite a user's output folder during a diagnostic run.
    output.mkdir(parents=True, exist_ok=False)
    application = QApplication([])
    for filename in ('segoeui.ttf', 'segoeuib.ttf'):
        font_path = Path('C:/Windows/Fonts') / filename
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))
    application.setFont(QFont('Segoe UI', 9))
    classic.apply_theme(application)
    window = app.Window()
    try:
        # The portable build must include the reference overlays and the same
        # instrument lettering used by editable exports.
        assert sum('legend_reference' in d for d in pidcore.CATALOG.values()) == 81
        import connection_policy
        attachment_document = pidcore.new_document()
        attachment_component = pidcore.component('turbine',0,0,attachment_document)
        attachment_document['components'].append(attachment_component)
        assert 'does not support new line connections' in connection_policy.attachment_reason(
            attachment_document, {'component':attachment_component['id'],'port':'shaft'})
        test_instrument = pidcore.component('pressure_transmitter',0,0,pidcore.new_document())
        test_instrument['tag'] = 'PT-203'
        instrument_svg = drawio_export.artwork(test_instrument).decode('utf-8')
        assert '>PT<' in instrument_svg and '>203<' in instrument_svg
        import component_legend
        legend_document = pidcore.new_document()
        legend_document['components'].append(test_instrument)
        for kind in ('foot_valve','relief_valve','radar_level_transmitter','thermal_mass_flowmeter'):
            assert pidcore.CATALOG[kind].get('symbol_reference')
            assert not pidcore.CATALOG[kind].get('legend_reference')
            legend_document['components'].append(pidcore.component(kind,0,0,legend_document))
        component_legend.export(legend_document, output / 'component-legend.svg')
        from PySide6.QtSvg import QSvgRenderer
        assert QSvgRenderer(str(output / 'component-legend.svg')).isValid()
        import xml.etree.ElementTree as ET
        legend_root = ET.parse(output / 'component-legend.svg').getroot()
        legend_info = json.loads(legend_root.find('{http://www.w3.org/2000/svg}metadata').text)
        assert len(legend_info['library_sha256']) == 64
        assert set(legend_info['types']) == {'pressure_transmitter','foot_valve','relief_valve',
                                          'radar_level_transmitter','thermal_mass_flowmeter'}
        window.example()
        envelope = custom_symbols.fixture()
        assert symbol_library.apply_definition(window,envelope)
        window.add_symbol(envelope['kind'],QPointF(0,180))
        assert window.document['symbol_definitions'][envelope['kind']] == envelope['definition']
        window.show()
        application.processEvents()
        original = copy.deepcopy(window.document)
        symbol = next(iter(window.symbols.values()))
        identifier = symbol.record['id']
        symbol.setSelected(True)
        assert editing.nudge(window, 10, 0)
        window.rotate()
        assert window.symbols[identifier].isSelected()
        window.undo()
        window.undo()
        assert window.document == original
        line = window.document['connections'][0]
        destination = window.document['components'][-1]
        assert editing.begin_reconnect(window,line['id'],'to')
        window.connect_port(destination['id'],'inlet')
        assert window.document['connections'][0]['to']['component'] == destination['id']
        window.undo()
        assert window.document == original
        assert all(not pipe.route_error for pipe in window.pipes)
        # Exercise the packaged viewport dispatch, not just connect_port().
        window.fit()
        application.processEvents()
        viewport = window.view.viewport()
        endpoints = original['connections'][0]
        positions = [window.view.mapFromScene(window.symbols[endpoints[end]['component']].port(endpoints[end]['port']))
                     for end in ('from','to')]
        assert all(viewport.rect().contains(position) for position in positions)
        def mouse_event(kind, position, button, buttons):
            event = QMouseEvent(kind, QPointF(position), QPointF(viewport.mapToGlobal(position)),
                                button, buttons, Qt.KeyboardModifier.NoModifier)
            application.sendEvent(viewport,event)
            application.processEvents()
        for drag in (False,True):
            if drag:
                mouse_event(QEvent.Type.MouseButtonPress,positions[0],Qt.MouseButton.LeftButton,Qt.MouseButton.LeftButton)
                mouse_event(QEvent.Type.MouseMove,positions[1],Qt.MouseButton.NoButton,Qt.MouseButton.LeftButton)
                mouse_event(QEvent.Type.MouseButtonRelease,positions[1],Qt.MouseButton.LeftButton,Qt.MouseButton.NoButton)
            else:
                for position in positions:
                    mouse_event(QEvent.Type.MouseButtonPress,position,Qt.MouseButton.LeftButton,Qt.MouseButton.LeftButton)
                    mouse_event(QEvent.Type.MouseButtonRelease,position,Qt.MouseButton.LeftButton,Qt.MouseButton.NoButton)
            assert len(window.document['connections']) == len(original['connections'])+1
            created = window.document['connections'][-1]
            assert created['from'] == endpoints['from'] and created['to'] == endpoints['to']
            assert window.selected.record['id'] == created['id']
            assert window.pending is None
            window.undo()
            assert window.document == original
        proposal = {'contract_version':1,'base_fingerprint':operations.fingerprint(window.document),
                    'operations':[], 'review_findings':[{'id':'smoke-check','message':'Verify example drawing',
                                                       'region':None,'object_ids':[]}]}
        # Synthetic metadata exercises the bundled schema and history without
        # making an API call or loading credentials.
        body = openai_bridge.request_body(window.document,'Offline packaged test','offline-test-model')
        generation = generation_provenance.finish(
            generation_provenance.capture(window.document,body,json.dumps(body).encode()),
            {'id':'offline-test-response','model':'offline-test-model','usage':None})
        observed = []
        def approve():
            dialog = application.activeModalWidget()
            panel = dialog.findChild(SourceReview)
            button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Apply)
            observed.append(button.isEnabled())
            panel.list.item(0).setCheckState(Qt.CheckState.Checked)
            observed.append(button.isEnabled())
            button.click()
        QTimer.singleShot(100,approve)
        assert sketch.review(window,proposal,generation=generation)
        assert observed == [False,True]
        assert window.document['review_history'][-1]['acknowledged_ids'] == ['smoke-check']
        assert window.document['review_history'][-1]['generation'] == generation
        pidcore.save(window.document, output / 'drawing.pid')
        assert pidcore.load(output / 'drawing.pid') == window.document
        window.saved = copy.deepcopy(window.document)
        assert window.open_path(output / 'drawing.pid')
        dialog = recovery.RecoveryDialog(window,output)
        assert dialog.tree.topLevelItemCount() == 1 and dialog.open_button.isEnabled()
        dialog.close()
        history = review_history.HistoryDialog(window)
        assert 'stored content: yes' in history.details.toPlainText()
        assert 'offline-test-response' in history.details.toPlainText()
        history.show()
        application.processEvents()
        history.grab().save(str(output/'review-history.png'))
        history.close()
        context = operations.context(window.document)
        assert context['instructions'] and context['document_schema']
        assert envelope['kind'] in context['catalog']
        assert envelope['kind'] in openai_bridge.wire_schema(window.document)['properties']['components']['items']['properties']['type']['enum']
        library = symbol_library.LibraryDialog(window)
        library.show()
        application.processEvents()
        assert library.preview()
        library.grab().save(str(output/'symbol-library.png'))
        library.close()
        assert len(pidcore.CATALOG) >= 141
        catalog_dialog = component_browser.CatalogDialog(window)
        catalog_dialog.show()
        application.processEvents()
        assert not catalog_dialog.insert.isEnabled()
        catalog_dialog.grab().save(str(output/'component-folders.png'))
        catalog_dialog.search.setText('shell tube')
        application.processEvents()
        catalog_dialog.grab().save(str(output/'component-catalog.png'))
        before_insert = copy.deepcopy(window.document)
        catalog_dialog.insert_component()
        assert window.document['components'][-1]['type'] == 'shell_tube_exchanger'
        window.undo()
        assert window.document == before_insert
        connection_dialog = connection_editor.ConnectionDialog(window,window.document['connections'][0]['id'])
        connection_dialog.show()
        application.processEvents()
        assert connection_dialog.candidate()['from'] == window.document['connections'][0]['from']
        connection_dialog.grab().save(str(output/'connection-editor.png'))
        connection_dialog.reject()
        file_menu = next(action.menu() for action in window.menuBar().actions() if action.text() == 'File')
        file_menu.popup(window.mapToGlobal(window.rect().topLeft()))
        application.processEvents()
        file_menu.grab().save(str(output/'file-menu.png'))
        file_menu.close()
        (output / 'authoring-context.json').write_text(json.dumps(context, indent=2), encoding='utf-8')
        window.export_to(output / 'drawing.svg')
        drawio_export.export(window, output / 'drawing.drawio')
        deliverables.export_sheet(window, output / 'drawing.pdf')
        deliverables.export_sheet(window, output / 'drawing.png')
        assert not QImage(str(output / 'drawing.png')).isNull()
        pdf = QPdfDocument()
        assert pdf.load(str(output / 'drawing.pdf')) == QPdfDocument.Error.None_
        assert pdf.pageCount() == 1
        assert 'TK-101' in pdf.getAllText(0).text()
        pdf.close()
        window.grab().save(str(output / 'workbench.png'))
        preview = sheet_preview.render_image(window)
        assert preview == QImage(str(output / 'drawing.png')).convertToFormat(preview.format())
        tabs = window.centralWidget().findChild(QTabWidget)
        tabs.setCurrentWidget(window.sheet_preview)
        application.processEvents()
        window.sheet_preview.fit()
        window.grab().save(str(output / 'sheet-preview.png'))
        (output / 'result.json').write_text(json.dumps({'passed': True, 'frozen': bool(getattr(sys, 'frozen', False)), 'checks': ['window startup', 'nudge and rotate', 'pipe reconnection', 'viewport click and drag connections', 'new connection selection', 'undo fidelity', 'example routes clear', 'review acknowledgment gate', 'review history roundtrip', 'recovery browser', 'direct file open', 'document roundtrip', 'schema and AI instructions', 'SVG', 'draw.io', 'PDF readable text', 'PNG load', 'sheet preview matches export']}), encoding='utf-8')
    finally:
        window.saved = window.document.copy()
        window.close()


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--smoke-test':
        try:
            smoke_test(sys.argv[2])
        except Exception:
            import traceback
            from pathlib import Path
            with Path(sys.argv[2] + '.error.txt').open('x', encoding='utf-8') as report:
                report.write(traceback.format_exc())
            sys.exit(1)
    else:
        import argparse
        parser = argparse.ArgumentParser(description='PID Studio drawing editor')
        parser.add_argument('document',nargs='?',help='Local .pid drawing to open')
        arguments = parser.parse_args()
        import app
        app.main(arguments.document)
