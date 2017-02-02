Installation
============


Prerequisites
-------------

- `Kivy 1.9+ <http://kivy.org/#download>`_
- The following Python modules (available via pip):
    - `watchdog <http://pythonhosted.org/watchdog/>`_
    - `Pygments <http://pygments.org/>`_
    - `docutils <http://docutils.sourceforge.net/>`_
    - `jedi <http://jedi.jedidjah.ch/en/latest/>`_
    - `gitpython <http://gitpython.readthedocs.org>`_
    - `six <https://pythonhosted.org/six/>`_
    - `kivy-garden <http://kivy.org/docs/api-kivy.garden.html>`_
- The XPopup widget from the [Kivy garden](https://github.com/kivy-garden/garden.xpopup)

Installation
------------

Download the Kivy Designer's source code:

::

    git clone http://github.com/kivy/kivy-designer/

or, download it manually from https://github.com/kivy/kivy-designer/archive/master.zip and extract to
`kivy-designer`

Open the downloaded folder and install the required prerequisites:

::

    cd kivy-designer
    pip install -Ur requirements.txt

To install the XPopup enter a console (on Windows use kivy.bat in the kivy folder):

::

    garden install xpopup

With the prerequisites installed, you can use the designer:

::

    python -m designer

On OS X you might need to use `kivy` command instead of `Python` if you are using our portable package.
