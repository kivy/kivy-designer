Kivy Designer
=============

**WARNING:** This project is at an unstable alpha stage and is not yet 
suitable for general use. There is no current plan for continuing the
development of Kivy Designer. **The repository has been archived,
please contact us if you intend to maintain the project.**

Kivy Designer is Kivy's tool for designing graphical user interfaces
(GUIs) from Kivy Widgets. You can compose and customize widgets, and
test them. It is completely written in Python using Kivy.

[![Build Status](https://travis-ci.org/kivy/kivy-designer.svg?branch=master)](https://travis-ci.org/kivy/kivy-designer)

Prerequisites
-------------

- [Kivy >= 1.9.1](http://kivy.org/#download)
- The following Python modules (available via pip):
    - [watchdog](https://pythonhosted.org/watchdog/)
    - [pygments](http://pygments.org/)
    - [docutils](http://docutils.sourceforge.net/)
    - [jedi](http://jedi.jedidjah.ch/en/latest/)
    - [gitpython](http://gitpython.readthedocs.org)
    - [six](https://pythonhosted.org/six/)
    - [kivy-garden](http://kivy.org/docs/api-kivy.garden.html)
- The XPopup widget from the [Kivy garden](https://github.com/kivy-garden/garden.xpopup)

Installation
------------

To install the prerequisites, enter a console (on Windows use kivy.bat in the kivy folder):

    pip install -U watchdog pygments docutils jedi gitpython six kivy-garden

or simple run:

    pip install -Ur requirements.txt

To install the XPopup enter a console (on Windows use kivy.bat in the kivy folder):

    garden install xpopup

With the prerequisites installed, you can use the designer:

    git clone http://github.com/kivy/kivy-designer/

or download it manually from https://github.com/kivy/kivy-designer/archive/master.zip and extract to
`kivy-designer`, and then run:

    cd kivy-designer
    python -m designer

On OS X you might need to use the `kivy` command instead of `python` if you are using our portable package.

If you're successful, you'll see something like this:

![ScreenShot](https://raw.github.com/kivy/kivy-designer/master/kivy_designer.png)

Support
-------

If you need assistance, you can ask for help on our mailing list:

* User Group : https://groups.google.com/group/kivy-users
* Email      : kivy-users@googlegroups.com

We also have an IRC channel:

* Server  : irc.freenode.net
* Port    : 6667, 6697 (SSL only)
* Channel : #kivy

Contributing
------------

We love pull requests and discussing novel ideas. Check out our
[contribution guide](http://kivy.org/docs/contribute.html) and
feel free to improve Kivy Designer.

The following mailing list and IRC channel are used exclusively for
discussions about developing the Kivy framework and its sister projects:

* Dev Group : https://groups.google.com/group/kivy-dev
* Email     : kivy-dev@googlegroups.com

IRC channel:

* Server  : irc.freenode.net
* Port    : 6667, 6697 (SSL only)
* Channel : #kivy-dev

License
-------

Kivy Designer is released under the terms of the MIT License. Please refer to the
LICENSE file.
