Kivy Designer Help
==================

Kivy Designer is Kivy's tool for designing Graphical User Interfaces (GUIs) from Kivy Widgets. You can compose and customize widgets, and test them.

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
* In Start Page, under "Recent Files" you will see recent projects. Click on any of them.

* Go to File->Recent Files.
* Click on the path, you want to open.

Features
--------
After opening a project, you will see following:
    * "Project Tree" on the left side, shows files and folders inside the project's directory.
    * "Toolbox" contains widgets which could be drag-drop to the required positions.
    * "UI Creator" is place where you will be designing your project. 
    * "Widget Tree" shows the Widget hierarchy of the project.
    * "Property Viewer" shows properties, their values and allows changing the values.
    * "Events" shows the available events and their event handler. You can change/set an event handler and add an event.
    * "KV Lang Area" shows what your kv file would be consisting.
    * "Kivy Console" is a console just like xterm, GNOME Terminal. You can enter commands and execute them.
    * "Python Shell" is an interactive Python Shell.
    * "Error Console" shows errors which may occur in the user code, while opening a project or creating custom widget.

Building a Project
------------------
After creating a new project or opening a project, next thing to do is to build your project. Here are number of available options through which you can create your project.

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
    
Run Project
~~~~~~~~~~~
Go to Run->Run Project, to run current project.

Project Preferences
-------------------
To access Project Preferences, go to Project->Project Preferences. Here you can access environment variables and arguments which must be passed to project to run it.

Kivy Designer Settings
----------------------
Kivy Designer Settings can be accessed by File->Settings. Here you can 
    * Modify Python Shell Path.
    * Modify whether to load changes in KV Lang Area automatically or not.
    * Number of Recent Files, Kivy Designer should keep track of.
    * Auto Save time out, after how many mins project should be saved automatically.
    
Auto Save
---------
Kivy Designer supports Auto Save. Your current project will be automatically saved after Auto Save Time out which is specified in Kivy Designer Settings. In case of any failure, you can access your last saved project from ".designer" folder present in the project's directory.

Detect Runtime Changes
----------------------
If a project has been changed outside Kivy Designer, then Kivy Designer will detect those changes. Kivy Designer will ask whether to reload the project or not.