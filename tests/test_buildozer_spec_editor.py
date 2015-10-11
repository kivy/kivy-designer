'''
File responsible for testing BuildozerSpecEditor
'''
import os

import unittest
from nose.tools import assert_equal
from designer.buildozer_spec_editor import BuildozerSpecEditor


class BuildozerSpecEditorTest(unittest.TestCase):

    def setUp(self):
        self.spec = BuildozerSpecEditor()
        self.spec.load_settings(os.path.realpath('tests'))

    def test_config_parser(self):
        c = self.spec.config_parser
        assert_equal(c.getdefault('app', 'title', ''), 'TestCase')
        assert_equal(c.getdefault('app', 'package.name', ''), 'test')
        assert_equal(c.getdefault('app', 'requirements', ''), 'kivy')
