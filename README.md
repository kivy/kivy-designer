Kivy Designer
=============

**WARNING:: This software was part of GSOC 2013, and is searching for a maintainer.**

Kivy Designer is Kivy's tool for designing Graphical User Interfaces
(GUIs) from Kivy Widgets. You can compose and customize widgets, and
test them. It is completely written in Python using Kivy.

Prerequisites
-------------

- [Kivy 1.8+](http://kivy.org/#download)
- The following Python modules (available via pip)
    - [watchdog](http://pythonhosted.org/watchdog/)
    - [Pygments](http://pygments.org/)
    - [docutils](http://docutils.sourceforge.net/)
- The FileBrowser widget from the [Kivy garden](http://kivy.org/docs/api-kivy.garden.html)



Installation
------------

To install the prerequisites, enter a console (on windows use kivy.bat in the kivy folder):

    pip install watchdog
    pip install pygments
    pip install docutils

To install the FileBrowser, enter a console (on windows use kivy.bat in the kivy folder):

    pip install kivy-garden
    garden install filebrowser

With the prerequisites installed, you can use the designer:

    git clone http://github.com/kivy/kivy-designer/
    cd kivy-designer
    python main.py

without git download, extract and execute main.py:
https://github.com/kivy/kivy-designer/archive/master.zip


On OS X you might need to use `kivy` command instead of `Python` if you are using our portable package.

If you're successful, you'll see something like this:

![ScreenShot](https://raw.github.com/kivy/kivy-designer/master/kivy_designer.png)
