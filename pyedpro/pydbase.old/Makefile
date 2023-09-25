#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#

.PHONY:  doc doc3 clean echo


PROG=pydbase

all:
	@echo "Type 'make help' for a list of targets"

.PHONY: tests

tests:
	cd tests; pytest
	cd ..

help:
	@echo
	@echo "Targets:"
	@echo "	 make install  -- Install ${PROG} (unofficial structure) obsolete"
	@echo "	 make setup    -- Run the setup.py script as install "
	@echo "	 make pack     -- package ${PROG}  "
	@echo "	 make remove   -- remove (all) traces of ${PROG}  from the system"
	@echo "	 make tests    -- execute test suite ${PROG}"
	@echo "	 make doc3     -- create ${PROG} documentation"
	@echo "	 make tests    -- execute ${PROG} test suite"
	@echo "	 make doxy     -- create ${PROG} documentation"
	@echo

# OLD install; use setup.py

#install:
#	@python3 ./install.py

setup:
	@python3 ./setup.py install

remove:
	@python3 ./setup.py install --record files.txt
	xargs rm -rf < files.txt
	@rm -f files.txt

pack:
	@./pack.sh

clean:
	rm -f *.pyc
	rm -f pedlib/*.pyc
	rm -rf pedlib/__pycache__
	rm -rf ../pycommon/__pycache__
	rm -f  ../pycommon/*.pyc

echo:
	@echo Echoing: ${CHECK}

# Auto Checkin
ifeq ("$(AUTOCHECK)","")
AUTOCHECK=autocheck
endif

DDD = $(shell bash -c 'read -p "Commit Message: " commit; echo $$commit')
#echo "Committing as $(DDD)"

pgit:
	git add .
	git commit -m "$(DDD)"
	git push
	#git push local

git:
	git add .
	git commit -m "$(AUTOCHECK)"
	git push
	git push local

doc:
	@pdoc --logo image.png  \
                -o doc `find . -maxdepth 2 -name  \*.py`

doc3:
	@pdoc3  --html --force -o doc3 `find . -maxdepth 2 -name  \*.py`

doxy:
	doxygen

# End of Makefile
