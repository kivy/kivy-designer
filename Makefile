PYTHON = python
CHECKSCRIPT = tools/pep8checker/pep8kivy.py
KIVY_DIR = 
KIVY_USE_DEFAULTCONFIG = 1
HOSTPYTHON = $(KIVYIOSROOT)/tmp/Python-$(PYTHON_VERSION)/hostpython
IOSPATH := $(PATH):/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin

hook:
	# Install pre-commit git hook to check your changes for styleguide
	# consistency.
	cp tools/pep8checker/pre-commit.githook .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
