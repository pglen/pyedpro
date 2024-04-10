# Limited

.PHONY: docs ver clean

all:
	@echo Targets: clean package docs

clean:
	@-find . -name "__pycache__" -exec rm -rf {} \;
	@-find . -name "*.pyc" -exec rm -rf {} \;
	@-rm -rf ./build/*
	@-rm -rf ./dist/*

package:
	pyinstaller pyedpro.spec --distpath ../../largefiles/pyedpro_packed

PPP=PYTHONPATH=pedlib:./:../pycommon  python -W ignore::DeprecationWarning `which pdoc` --force --html

docs:
	@${PPP} -o pedlib/docs pyedpro.py
	@${PPP} -o pedlib/docs pedlib/pedweb.py
	@${PPP} -o pedlib/docs pedlib/parser.py
	@${PPP} -o pedlib/docs pedlib/pedthread.py
	@${PPP} -o pedlib/docs pedlib/pedbuffs.py
	@${PPP} -o pedlib/docs pedlib/notesql.py
	@${PPP} -o pedlib/docs pedlib/peddoc.py
	@${PPP} -o pedlib/docs pedlib/pedtask.py
	@${PPP} -o pedlib/docs pedlib/lexer.py
	@${PPP} -o pedlib/docs pedlib/peddoc_diff.py
	@${PPP} -o pedlib/docs pedlib/acthand.py
	@${PPP} -o pedlib/docs pedlib/importer.py
	@${PPP} -o pedlib/docs pedlib/keyhand.py
	@${PPP} -o pedlib/docs pedlib/keywords.py
	@${PPP} -o pedlib/docs pedlib/leven.py
	@${PPP} -o pedlib/docs pedlib/pedcal.py
	@${PPP} -o pedlib/docs pedlib/pedcanv.py
	@${PPP} -o pedlib/docs pedlib/pedcolor.py
	@${PPP} -o pedlib/docs pedlib/pedconfig.py
	@${PPP} -o pedlib/docs pedlib/peddlg.py
	@${PPP} -o pedlib/docs pedlib/peddraw.py
	@${PPP} -o pedlib/docs pedlib/pedfind.py
	@${PPP} -o pedlib/docs pedlib/pedfont.py
	@${PPP} -o pedlib/docs pedlib/pedgoto.py
	@${PPP} -o pedlib/docs pedlib/pedlcmd.py
	@${PPP} -o pedlib/docs pedlib/pedlog.py
	@${PPP} -o pedlib/docs pedlib/pedmenu.py
	@${PPP} -o pedlib/docs pedlib/pedmisc.py
	@${PPP} -o pedlib/docs pedlib/pednotes.py
	@${PPP} -o pedlib/docs pedlib/pedobjs.py
	@${PPP} -o pedlib/docs pedlib/pedofd.py
	@${PPP} -o pedlib/docs pedlib/pedoline.py
	@${PPP} -o pedlib/docs pedlib/pedplug.py
	@${PPP} -o pedlib/docs pedlib/pedspell.py
	@${PPP} -o pedlib/docs pedlib/pedsql.py
	@${PPP} -o pedlib/docs pedlib/pedstruct.py
	@${PPP} -o pedlib/docs pedlib/pedtdlg.py
	@${PPP} -o pedlib/docs pedlib/pedtts.py
	@${PPP} -o pedlib/docs pedlib/pedui.py
	@${PPP} -o pedlib/docs pedlib/pedundo.py
	@${PPP} -o pedlib/docs pedlib/pedutil.py
	@${PPP} -o pedlib/docs pedlib/pedwin.py
	@${PPP} -o pedlib/docs pedlib/pedxtnd.py
	@${PPP} -o pedlib/docs pedlib/pedync.py
	@${PPP} -o pedlib/docs pedlib/stack.py
	@${PPP} -o pedlib/docs pedlib/webwin.py

pipup:
	@# Prep
	cp ../README.md README.md
	./pip-build.py
	./pip-upload.sh

# EOF
