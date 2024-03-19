# Limited

clean:
	-find . -name "__pycache__" -exec rm -r {} \;
	-find . -name "*.pyc" -exec rm -r {} \;
	-rm -rf ./build/*
	-rm -rf ./dist/*

package:
	pyinstaller pyedpro.spec --distpath ../pyedpro_packed

# EOF
