
# Limited

all:
	@echo Targets: clean package

clean:
	@-find . -name "__pycache__" -exec rm -rf {} \;
	@-find . -name "*.pyc" -exec rm -rf {} \;
	@-rm -rf ./build/*
	@-rm -rf ./dist/*

package:
	pyinstaller pyedpro.spec --distpath ../../largefiles/pyedpro_packed

# EOF
