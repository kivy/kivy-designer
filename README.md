Kivy Designer
=============

**WARNING::This is Alpha grade software, don't blame us if it eats
  your kittens**

Kivy Designer is Kivy's tool for designing Graphical User Interfaces
(GUIs) from Kivy Widgets. You can compose and customize widgets, and
test them. It is completely written in Python using Kivy.

Installation
------------

Prequisites:

- Kivy 1.8+
- The Python watchdog module, http://pythonhosted.org/watchdog/
- The FileBrowser widget from the [Kivy garden](http://kivy.org/docs/api-kivy.garden.html)

To install the FileBrowser start kivy.bat (in the kivy folder) and enter:

    pip install kivy-garden
    garden install filebrowser
    
With the prequisites installed, you can use the designer:
    
    git clone http://github.com/kivy/kivy-designer/
    cd kivy-designer
    python main.py

without git download, extract and execute main.py:
https://github.com/kivy/kivy-designer/archive/master.zip


On OsX you might need to use `kivy` command instead of `Python` if you are using our portable package.


![ScreenShot](https://raw.github.com/kivy/kivy-designer/master/kivy_designer.png)
