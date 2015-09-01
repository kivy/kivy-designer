Kivy Designer Help
==================

Kivy Designer is Kivy's tool for designing Graphical User Interfaces (GUIs) from Kivy Widgets. You can compose and customize widgets, and test them. It is completely written in Python using Kivy. Kivy Designer is integrated with Buildozer and Hanga, so you can easily develop and publish your applications to Desktop and Mobile devices.

Kivy Designer Documentation
---------------------------

This help is a simple offline overview of Kivy Designer. Read the full docs at http://kivy-designer.readthedocs.org/

Project
-------
A Project is what you would be working on. Each project contains atleast one 'kv' file and one 'py' file. For your project to be compatible completely with Kivy Designer, it will be good to start creating it from Kivy Designer.

Kivy Designer Start Page
------------------------
When you will start Kivy Designer, then first screen you will see is "Start Page" of Kivy Designer. It contains four buttons "Open Project", "New Project", "Kivy" and "Kivy Designer" and it shows recently open projects, click on any of them to open.

Create New Project
------------------
To create a new project:
    * Click File->New Project.
    * Select any of the desired templates from the popup.
    * Click "New" to create a new project.

Open a Project
--------------
To open a project:
    * Click on File->Open Project
    * Navigate to the path of project.
    * If you wish then select any 'kv' file.
    * Click "Open" to open project.
    
Open Recent Project
---------------------
* Open a Recent Project using Start Page
* In Start Page, under "Recent Projects" you will see recent projects. Click on any of them.

* Go to File->Recent Projects.
* Click on the path, you want to open.

Kivy Designer Interface
-----------------------

This is a list and overview of some Kivy Designer's components

After opening a project, you will see following:
    1. **Project Tree** on the left side, shows files and folders inside the project's directory.
    2. **Toolbox** contains widgets which could be drag-drop to the required positions.
    3. **UI Creator** is place where you will be designing your project.
    4. **Widget Tree** shows the Widget hierarchy of the project.
    5. **Property Viewer** shows properties, their values and allows changing the values.
    6. **Events** shows the available events and their event handler. You can change/set an event handler and add an event.
    7. **KV Lang Area** shows what your kv file would be consisting.
    8. **Kivy Console** is a console just like xterm, GNOME Terminal. You can enter commands and execute them.
    9. **Python Shell** is an interactive Python Shell.
    10. **Error Console** shows errors which may occur in the user code, while opening a project or creating custom widget.
    11. **Playground Settings** you can change the playground screen size, orientation and zoom to help the UI development
    12. **Status Bar** The status bar helps you displaying the selected widget hierarchy and messages.

UI Creator
----------

You'll probably spend a big part of your time designing the app interface; so the UI creator is the right place for you :)
When designing the UI, you can get Widget from **Widget Tree** or you insert the KV Lang code in **KV Lang Area**
If you want to change the size or orientaiton of the emulated interface, you can set it on **Playground Settings**

Adding Widget
~~~~~~~~~~~~~~
* Click on "Toolbox" in the left of the screen.
* A number of Widgets will be shown.
* Press the Widget which you want to add.
* Drag to the parent on which you want to add the widget. While dragging you can also see how it is going to look when added to that parent.
* Drop the widget when desired.

Similarly WidgetTree also supports drag-drop of widgets. Select any widget from WidgetTree or drag any widget from WidgetTree and drop it on the parent widget.

Changing Property Value of a Widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Select a Widget by clicking on it.
* On the bottom-right side you can see Widgets with its properties. To change the value, just enter the value.

Setting Event Handler
~~~~~~~~~~~~~~~~~~~~~
* Select a Widget.
* On the bottom-right side, select "Events".
* You can current available events of widget. 
* To enter Event Handler, set the value of event handler in its corresponding text.
* While entering an id and dot '.', you will see a dropdown with available functions.
* If selected widget is a custom widget, then you can create a new event by entering event name in the last text and saving the project.

Open Project's Python Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Click on "Project Tree" on left side.
* Click on the file name you want to open.
* File will be opened in a new tab.

Edit Options
~~~~~~~~~~~~
Edit Options are available for Widgets and also for text in KVLangArea and Python Files. Select a Widget or click on KVLangArea or to see its available options.
    * Cut, delete the current widget/selected text from its position.
    * Copy, copies the current widget/selected text.
    * Paste, add the widget/text to parent widget/KV Lang Area or Python File
    * Select All, selects all widgets/text.
    * Delete, delete current selected widget/text.
    * Find, available on Text files. You can search using a string or regex.
    
Moreover you can also access these options using keyboard shortcuts.

Saving Project
~~~~~~~~~~~~~~
After creating a project you can save project by File->Save or File->Save As

Add Files to Project
~~~~~~~~~~~~~~~~~~~~
You can also add files to a project.
    * Go to Project->Add File.
    * Click on "Open File" to open the file you want to add.
    * Click on "Open Folder" to open the folder where you want to add file inside project.
    * Check "Always use this folder" if you want to always use this folder for this file type.
    * Click "Add" to Add File.
    
Add Custom Widgets to Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can also add custom widgets to project.
    * Go to Project->Add Custom Widget.
    * Select custom widget's python file.
    * Click "Open"

Building
--------

To build, and run your project, you'll need to configure the Kivy Designer Builder. The Builder will help you to target your application to the desired platforms.
You can access Builder settings at ``Run -> Edit Profiles...``

.. _Builder:

Builders
~~~~~~~~
You can use the following tools to build your project:

    * **Desktop** - This is the default Python interpreter available in your system. (Desktop only)
    * **Buildozer** - Use `Buildozer <http://buildozer.readthedocs.org/>`_ to target mobile devices. (Android and iOS)
    * **Hanga** - Use Hanga to target mobile devices. (Android)

Build Profiles
~~~~~~~~~~~~~~
You can select and configure your Builder using Build Profiles. 

Kivy Designer already provides 3 defaults profiles:

    * Desktop
    * Android - Buildozer
    * iOS - Buildozer

You can edit/delete these profiles and create new ones. To use a profile, click in the button ``Use this profile`` or select the profile from the menu ``Run -> Select Profile``

Editing a profile
~~~~~~~~~~~~~~~~~

Before edit a build profile, it's a good idea to know what you are editing :) Take a look on what each field represents

    * **Name** - Name of the profile. This name will be visible in the profiles list.
    * **Builder** - Select which Builder_ do you want to use.
    * **Target** - Select the target platform. IMPORTANT: Just make sure that the selected Builder_ supports the desired platform.
    * **Mode** - Used by Buildozer and Hanga only. This sets the build mode, Debug or Release.
    * **Install On Device** - If you are targeting a mobile device, this tool allows you to auto install the application every build.
    * **Debug** - If activated and targeting Android, will show the logcat output on Kivy Console.
    * **Verbose** - If activated, will run your Builder_ on verbose mode.

Run
~~~

The ``Run`` menu provides you some options. Take a look in the table bellow to see how it works with each Builder_

+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
|           | **Desktop**                           | **Buildozer**                              | **Hanga**                                |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
| **Run**   | Run *main.py* with Python interpreter | Build, install and run on target device    | Not yet implemented                      |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
| **Stop**  | Stop the Python interpreter           | Nothing                                    | Not yet implemented                      |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
| **Clean** | Removes all .pyc and __pycache__      | Clean the Buildozer build                  | Not yet implemented                      |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
| **Build** | Generate .pyc                         | Build the project. If ``Install On Device``| Not yet implemented                      |
|           |                                       | is set, install it on device.              |                                          |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
|**Rebuild**| Run ``Clean`` and the ``Build``       | Run ``Clean`` and the ``Build``            | Not yet implemented                      |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+

Modules
-------

While developing your application, Kivy provides some `extra modules <http://kivy.org/docs/api-kivy.modules.html>`_ to help you.

Kivy Designer has an interface to some of `these modules <http://kivy.org/docs/api-kivy.modules.html>`_ .

To use Kivy Modules you must target Desktop, select the desired module at ``Run -> Run with module...``.

Screen Emulation
~~~~~~~~~~~~~~~~

It's really important to see your application running in different screen sizes, dimensions and orientations.

Kivy Designer provides a simple interface to the `Screen Module <http://kivy.org/docs/api-kivy.modules.screen.html#module-kivy.modules.screen>`_.

This module provides some settings. You can change the ``Device``, ``Orientation`` and ``Scale``. And the just press ``Run`` to run your application with Screen Module.

Touchring
~~~~~~~~~

The `Touchring Module <http://kivy.org/docs/api-kivy.modules.touchring.html#module-kivy.modules.touchring>`_ shows rings around every touch on the surface / screen.

You can use this module to check that you don’t have any calibration issues with touches.

Monitor
~~~~~~~

The `Monitor Module <http://kivy.org/docs/api-kivy.modules.monitor.html#module-kivy.modules.monitor>`_ is a toolbar that shows the activity of your current application.

Inspector
~~~~~~~~~

.. note::
    `This module is highly experimental, use it with care.`

The `Inspector Module <http://kivy.org/docs/api-kivy.modules.inspector.html#module-kivy.modules.inspector>`_ is a tool for finding a widget in the widget tree by clicking or tapping on it.

After running your app, you can access the Inspector with:

    - "Ctrl + e": activate / deactivate the inspector view
    - "Escape": cancel widget lookup first, then hide the inspector view

Available inspector interactions:

    - tap once on a widget to select it without leaving inspect mode
    - double tap on a widget to select and leave inspect mode (then you can manipulate the widget again)

.. warning::
    Some properties can be edited live. However, due to the delayed usage of some properties, it might crash if you don’t handle all the cases.

Web Debugger
~~~~~~~~~~~~

The `Web Debugger Module <http://kivy.org/docs/api-kivy.modules.webdebugger.html#module-kivy.modules.webdebugger>`_ starts a webserver and run in the background. You can see how your application evolves during runtime, examine the internal cache etc.

To access the debugger, Kivy Designer will open http://localhost:5000/

Project Preferences
-------------------
To access Project Preferences, go to Project->Project Preferences. Here you can access environment variables and arguments which must be passed to project to run it.

Kivy Designer Settings
----------------------
Kivy Designer Settings can be accessed by File->Settings. Here you can 
    * Modify Python Shell Path.
    * Modify Buildozer Path
    * Enable/Disable the option to auto create the buildozer.spec
    * Modify whether to load changes in KV Lang Area automatically or not.
    * Number of Recent Files, Kivy Designer should keep track of.
    * Auto Save time out, after how many mins project should be saved automatically.
    
Auto Save
---------
Kivy Designer supports Auto Save. Your current project will be automatically saved after Auto Save Time out which is specified in Kivy Designer Settings. In case of any failure, you can access your last saved project from ".designer" folder present in the project's directory.

Detect Runtime Changes
----------------------
If a project has been changed outside Kivy Designer, then Kivy Designer will detect those changes. Kivy Designer will ask whether to reload the project or not.