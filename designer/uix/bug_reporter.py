from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.clipboard import Clipboard
import webbrowser
import six.moves.urllib
import os

Builder.load_string('''
<BugReporter>:
    txt_traceback: txt_traceback
    Image:
        source: 'data/logo/kivy-icon-256.png'
        opacity: 0.2
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        Label:
            id: title
            text: 'Sorry, Kivy Designer has experienced an internal error :('
            font_size: '16pt'
            halign: 'center'
            size_hint_y: None
            height: '30pt'
        Label:
            id: subtitle
            text: 'You can report this bug using the button bellow, ' \
                    'helping us to fix it.'
            text_size: self.size
            font_size: '11pt'
            halign: 'center'
            valign: 'top'
            size_hint_y: None
            height: '30pt'
        ScrollView:
            id: e_scroll
            bar_width: 10
            scroll_y: 0
            TextInput:
                id: txt_traceback
                size_hint_y: None
                height: max(e_scroll.height, self.minimum_height)
                background_color: 1, 1, 1, 0.05
                text: ''
                foreground_color: 1, 1, 1, 1
                readonly: True
        BoxLayout:
            size_hint: 0.5, None
            padding: 10, 10
            height: 50
            pos_hint: {'x':0.25}
            spacing: 5
            Button:
                text: 'Copy to clipboard'
                on_press: root.on_clipboard()
            Button:
                text: 'Report Bug'
                on_press: root.on_report()
''')


class BugReporter(FloatLayout):
    txt_traceback = ObjectProperty(None)
    '''TextView to show the traceback message
    '''

    def on_clipboard(self, *args):
        '''Event handler to "Copy to Clipboard" button
        '''
        Clipboard.copy(self.txt_traceback.text)

    def on_report(self, *args):
        '''Event handler to "Report Bug" button
        '''
        txt = six.moves.urllib.parse.quote(self.txt_traceback.text)
        url = 'https://github.com/kivy/kivy-designer/issues/new?body=' + txt
        webbrowser.open(url)


class BugReporterApp(App):

    title = "Kivy Designer - Bug reporter"
    traceback = ''

    def __init__(self, traceback):
        self.traceback = traceback
        super(BugReporterApp, self).__init__()

    def build(self):
        rep = BugReporter()
        template = '''
## Environment Info

%s

## Traceback

%s

'''
        env_info = 'Pip is not installed'
        try:
            from pip.req import parse_requirements
            from pip.download import PipSession
            import platform

            requirements = parse_requirements(os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '..',
                '..',
                'requirements.txt'),
                session=PipSession()
            )
            env_info = ''
            for req in requirements:
                version = req.installed_version
                if version is None:
                    version = 'Not installed'
                env_info += req.name + ': ' + version + '\n'
            env_info += '\nPlatform: ' + platform.platform()
            env_info += '\nPython: ' + platform.python_version()

        except ImportError:
            pass
        rep.txt_traceback.text = template % (env_info, self.traceback)

        return rep


if __name__ == '__main__':
    BugReporterApp('Bug example').run()
