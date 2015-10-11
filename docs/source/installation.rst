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
- The ``FileBrowser`` widget from the `Kivy Garden <http://kivy.org/docs/api-kivy.garden.html>`_


Installation
------------

Download the Kivy Designer's source code:

::

    git clone http://github.com/kivy/kivy-designer/

or, without git download: https://github.com/kivy/kivy-designer/archive/master.zip

Open the downloaded folder and install the required prerequisites:

::

    cd kivy-designer
    pip install -r requirements.txt

To install the FileBrowser, enter a console (on windows use kivy.bat in the kivy folder):

::

    garden install filebrowser

With the prerequisites installed, you can use the designer:

::

    python main.py

On OS X you might need to use `kivy` command instead of `Python` if you are using our portable package.
