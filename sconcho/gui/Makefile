all:
	pyuic4 --from-imports -o ui_main_window.py ui/main_window.ui
	
# NOTE: this seems like a hack; pyuic4 should really offer a way
# to do this automagically
	sed -i -e '/from [a|c|p|r|s]/s/from /from sconcho.gui./' ui_main_window.py
	pyuic4 -o ui_export_bitmap_dialog.py ui/export_bitmap_dialog.ui
	pyuic4 -o ui_new_pattern_dialog.py ui/new_pattern_dialog.ui
	pyuic4 -o ui_sconcho_manual.py ui/sconcho_manual.ui
	pyuic4 -o ui_preferences_dialog.py ui/preferences_dialog.ui
	pyuic4 -o ui_manage_symbol_dialog.py ui/manage_symbol_dialog.ui
	pyuic4 -o ui_pattern_repeat_box_dialog.py ui/pattern_repeat_box_dialog.ui
	pyuic4 -o ui_update_dialog.py ui/update_dialog.ui
	pyuic4 -o ui_row_repeat_number_dialog.py ui/row_repeat_number_dialog.ui
	pyuic4 -o ui_num_row_column_dialog.py ui/num_row_column_dialog.ui
	pyrcc4 -py3 -o icons_rc.py icons.qrc


ctags:
	ctags *.py ../util/*.py

.PHONY: clean
clean:
	rm -f *.pyc ui_* icons_rc.py

