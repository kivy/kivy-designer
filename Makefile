PYTHON = python
CHECKSCRIPT = tools/pep8checker/pep8kivy.py
KIVY_DIR =
KIVY_USE_DEFAULTCONFIG = 1
HOSTPYTHON = $(KIVYIOSROOT)/tmp/Python-$(PYTHON_VERSION)/hostpython
IOSPATH := $(PATH):/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin
NOSETESTS = $(PYTHON) -m nose.core

hook:
	# Install pre-commit git hook to check your changes for styleguide
	# consistency.
	cp tools/pep8checker/pre-commit.githook .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

style:
	$(PYTHON) $(CHECKSCRIPT) .

stylereport:
	$(PYTHON) $(CHECKSCRIPT) -html .


test:
	-rm -rf kivy/tests/build
	$(NOSETESTS) tests

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  hook           add Pep-8 checking as a git precommit hook"
	@echo "  style          to check Python code for style hints."
	@echo "  style-report   make html version of style hints"
	@echo "  testing        make unittest (nosetests)"
