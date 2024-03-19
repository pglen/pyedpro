#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#

.PHONY:  doc doc3 clean prepimage

all:
	@echo "Targets: doc setup pack prepimage -- Type 'make help' more targets"

help:
	@echo
	@echo "Targets:"
	@echo "	 make install      -- Install PyEdPro (unofficial structure)"
	@echo "	 make setup        -- Run the setup.py script as install "
	@echo "	 make pack         -- package PyEdPro "
	@echo "	 make remove       -- remove (all) traces of pyedpro from the system"
	@echo "	 make doc          -- create documentation"
	@echo "	 make prepimage    -- create app image
	@echo

# OLD install; use setup.py

setup:
	@python3 ./setup.py install

remove:
	@python3 ./setup.py install --record files.txt
	xargs rm -rf < files.txt
	@rm -f files.txt

pack:
	@./pack.sh

clean:
	-find . -name "__pycache__" -exec rm -r {} \;
	-find . -name "*.pyc" -exec rm -r {} \;

# Auto Checkin
ifeq ("$(AUTOCHECK)","")
AUTOCHECK=autocheck
endif

git:
	git add .
	git commit -m "$(AUTOCHECK)"
	git push
#	git push local

doc:
	@PYTHONPATH=pedlib:pycommon pdoc --html --force -o doc pyedpro/pyedpro.py
	@PYTHONPATH=pedlib:pycommon pdoc --html --force -o doc pyedpro/pedlib/pedwin.py
	@#PYTHONPATH=pedlib:pycommon pdoc --html --force -o doc pyedpro/pedlib/peddoc.py

prepimage:
	./prepimage.sh

# End of Makefile
