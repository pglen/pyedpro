pygettext -d po/pyedpro  pyedpro.py pyedlib/pedmenu.py

msgmerge -U po/de_DE.po po/pyedpro.pot
msgmerge -U po/zh_CN.po po/pyedpro.pot

