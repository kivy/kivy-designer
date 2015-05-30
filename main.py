import traceback
from kivy.core.window import Window
from designer.app import DesignerApp
from designer.uix.bug_reporter import BugReporterApp

if __name__ == '__main__':
    try:
        DesignerApp().run()
    except Exception as e:
        for child in Window.children:
            Window.remove_widget(child)
        BugReporterApp(traceback.format_exc()).run()
