Kivy Designer
=============

Kivy Designer is Kivy's tool for designing graphical user interfaces
(GUIs) from Kivy Widgets. You can compose and customize widgets, and
test them. It is completely written in Python using Kivy.

[![Build Status](https://travis-ci.org/kivy/kivy-designer.svg?branch=master)](https://travis-ci.org/kivy/kivy-designer)

Prerequisites
-------------

- [Kivy 1.9+](http://kivy.org/#download)
- The following Python modules (available via pip):
    - [watchdog](https://pythonhosted.org/watchdog/)
    - [pygments](http://pygments.org/)
    - [docutils](http://docutils.sourceforge.net/)
    - [jedi](http://jedi.jedidjah.ch/en/latest/)
    - [gitpython](http://gitpython.readthedocs.org)
    - [six](https://pythonhosted.org/six/)
    - [kivy-garden](http://kivy.org/docs/api-kivy.garden.html)
- The FileBrowser widget from the [Kivy garden](http://kivy.org/docs/api-kivy.garden.html)


Installation
------------

To install the prerequisites, enter a console (on Windows use kivy.bat in the kivy folder):

    pip install -U watchdog pygments docutils jedi gitpython six kivy-garden

or simple run:

    pip install -r requirements.txt

To install the FileBrowser, enter a console (on Windows use kivy.bat in the kivy folder):

    garden install filebrowser

With the prerequisites installed, you can use the designer:

    git clone http://github.com/kivy/kivy-designer/
    cd kivy-designer
    python main.py

Without git, download, extract and execute main.py:

https://github.com/kivy/kivy-designer/archive/master.zip


On OS X you might need to use the `kivy` command instead of `python` if you are using our portable package.

If you're successful, you'll see something like this:

![ScreenShot](https://raw.github.com/kivy/kivy-designer/master/kivy_designer.png)
