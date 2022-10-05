#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#

all:
	@echo "Type 'make help' for a list of targets"

help:
	@echo
	@echo "Targets:"
	@echo "	 make install  -- Install PyEdPro (unofficial structure)"
	@echo "	 make setup    -- Run the setup.py script as install "
	@echo "	 make pack     -- package PyEdPro "
	@echo "	 make remove   -- remove (all) traces of pyedpro from the system
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

#CHECK=xxx

echo:
	@echo Echoing: ${CHECK}

# Auto Checkin
ifeq ("$(AUTOCHECK)","")
AUTOCHECK=autocheck
endif

git:
	git add .
	git commit -m "$(AUTOCHECK)"
	git push
	git push local

# End of Makefile
