all:
	pyuic4 -o ui_mainWindow.py ui/mainWindow.ui
	pyuic4 -o ui_insertDeleteRowColumnDialog.py ui/insertDeleteRowColumnDialog.ui
	pyuic4 -o ui_exportBitmapDialog.py ui/exportBitmapDialog.ui
	pyuic4 -o ui_newPatternDialog.py ui/newPatternDialog.ui
	pyuic4 -o ui_sconchoManual.py ui/sconchoManual.ui
	pyuic4 -o ui_preferencesDialog.py ui/preferencesDialog.ui
	pyuic4 -o ui_manageKnittingSymbolDialog.py ui/manageKnittingSymbolDialog.ui
	pyrcc4 -o icons_rc.py icons.qrc


.PHONY: clean
clean:
	rm -f *.pyc ui_* icons_rc.py

