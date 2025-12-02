#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#

.PHONY:  pack docs clean prepimage

all:
	@echo "Targets: docs setup pack prepimage -- Type 'make help' more targets"

help:
	@echo
	@echo "Targets:"
	@echo "	 make pipinstall   -- Run the pip setup.py script as install "
	@echo "	 make prepimage    -- create app image"
	@echo "	 make pack         -- package PyEdPro into parent dir (pyedpro.tgz)"
	@echo "	 make install      -- *Install PyEdPro (unofficial structure)"
	@echo "	 make remove       -- *remove (all) traces of pyedpro from the system"
	@echo "	 make docs         -- *create documentation (see pyedpro dir)"
	@echo
	@echo Targets marked with '*' are obsolete or moved or defective
	@echo

pipinstall:
	cp README.md pyedpro
	cd pyedpro; pip install .
	rm pyedpro/README.md

remove:
	@python3 ./setup.py install --record files.txt
	xargs rm -rf < files.txt
	@rm -f files.txt

pack:
	@./pack.sh

clean:
	-find . -name "__pycache__" -exec rm -r {} \;
	-find . -name "*.pyc" -exec rm -r {} \;
	-find . -name "build" -exec rm -r {} \;
	-find . -name "dist" -exec rm -r {} \;

# Auto Checkin
ifeq ("$(AUTOCHECK)","")
AUTOCHECK=autocheck
endif

git: clean
	git add .
	git commit -m "$(AUTOCHECK)"
	git push
#	git push local

docs:
	@echo plese see docs gen in the pyedpro directory

prepimage:
	./prepimage.sh

# End of Makefile
