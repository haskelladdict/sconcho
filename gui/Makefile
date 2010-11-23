all:
	pyuic4 -o ui_mainWindow.py ui/mainWindow.ui
	pyuic4 -o ui_insertDeleteRowColumnWidget.py ui/insertDeleteRowColumnWidget.ui
	pyuic4 -o ui_exportBitmapWidget.py ui/exportBitmapWidget.ui
	pyuic4 -o ui_newPatternWidget.py ui/newPatternWidget.ui
	pyrcc4 -o icons_rc.py icons.qrc


.PHONY: clean
clean:
	rm -f *.pyc ui_* icons_rc.py

