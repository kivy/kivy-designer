'''
This file is responsible for testing Apps inside the Kivy Designer project.
'''

import unittest

from kivy.clock import Clock
from kivy.properties import partial


class AppsTest(unittest.TestCase):

    def test_designer_app(self):
        from designer.app import DesignerApp
        d = DesignerApp()
        d.bind(started=partial(d.stop))
        d.run()

    def test_bug_reporter(self):
        from designer.uix.bug_reporter import BugReporterApp
        b = BugReporterApp('Exception message')
        Clock.schedule_once(b.stop, 1)
        b.run()
