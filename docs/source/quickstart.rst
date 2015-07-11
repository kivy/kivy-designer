Quick-start
===========

Let's know more about Kivy Designer!


How it works
------------

Kivy Designer organizes some open source tools to help you to create Kivy UI easily, develop your applications and target multiple platforms.


Kivy Designer Interface
-----------------------

This is a list and overview of some Kivy Designer's components

After opening a project, you will see following:
    * **Project Tree** on the left side, shows files and folders inside the project's directory.
    * **Toolbox** contains widgets which could be drag-drop to the required positions.
    * **UI Creator** is place where you will be designing your project. 
    * **Widget Tree** shows the Widget hierarchy of the project.
    * **Property Viewer** shows properties, their values and allows changing the values.
    * **Events** shows the available events and their event handler. You can change/set an event handler and add an event.
    * **KV Lang Area** shows what your kv file would be consisting.
    * **Kivy Console** is a console just like xterm, GNOME Terminal. You can enter commands and execute them.
    * **Python Shell** is an interactive Python Shell.
    * **Error Console** shows errors which may occur in the user code, while opening a project or creating custom widget.


Building
--------

To build, and run your project, you'll need to configure the Kivy Designer Builder. The Builder will help you to target your application to the desired platforms.

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

.. image:: https://cloud.githubusercontent.com/assets/4960137/8321449/648a15ee-19fd-11e5-9836-9cc715b8dbd7.png

Kivy Designer already provides 3 defaults profiles:

    * Desktop
    * Android - Buildozer
    * iOS - Buildozer

You can edit/delete these templates or create new ones. To use a profile, click in the button ``Use this profile`` or select the profile from the menu ``Run -> Select Profile``

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
| **Stop**  | Stop the Python interpreter           | If running a command, it's it.             | Not yet implemented                      |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
| **Clean** | Removes all .pyc and __pycache__      | Clean the Buildozer build                  | Not yet implemented                      |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
| **Build** | Generate .pyc                         | Build the project. If ``Install On Device``| Not yet implemented                      |
|           |                                       | is set, install it on device.              |                                          |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+
|**Rebuild**| Run ``Clean`` and the ``Build``       | Run ``Clean`` and the ``Build``            | Not yet implemented                      |
+-----------+---------------------------------------+--------------------------------------------+------------------------------------------+

Emulating different screen devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While developing your application, it's really important to see it running in different screen sizes. Kivy Designer provides a simple interface to the `Screen Module <http://kivy.org/docs/api-kivy.modules.screen.html#module-kivy.modules.screen>`_.

To use it, you must to target the Desktop, and then select the desired device on ``Run -> Screen Emulation``, and the orientation on ``Run -> Screen Orientation``.

And then just use ``Run -> Run`` to run the application in the selected simulated screen device.