import os
import sys
import webbrowser

import six.moves.urllib
from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup


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
            size_hint: 0.6, None
            padding: 10, 10
            height: 70
            pos_hint: {'x':0.2}
            spacing: 5
            Button:
                text: 'Copy to clipboard'
                on_press: root.on_clipboard()
            Button:
                text: 'Report Bug'
                on_press: root.on_report()
            Button:
                text: 'Close'
                on_press: root.on_close()

<ReportWarning>:
    size_hint: .5, .5
    auto_dismiss: False
    title: 'Warning'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text_size: self.size
            text: root.text
            padding: '4sp', '4sp'
            valign: 'middle'
        BoxLayout:
            Button:
                size_hint_y: None
                height: '40sp'
                on_release: root.dispatch('on_release')
                text: 'Report'
            Button:
                size_hint_y: None
                height: '40sp'
                on_release: root.dismiss()
                text: 'Close'
''')


class ReportWarning(Popup):
    text = StringProperty('')
    '''Warning Message
    '''

    __events__ = ('on_release',)

    def on_release(self, *args):
        pass


class BugReporter(FloatLayout):
    txt_traceback = ObjectProperty(None)
    '''TextView to show the traceback message
    '''

    def __init__(self, **kw):
        super(BugReporter, self).__init__(**kw)
        self.warning = None

    def on_clipboard(self, *args):
        '''Event handler to "Copy to Clipboard" button
        '''
        Clipboard.copy(self.txt_traceback.text)

    def on_report(self, *args):
        '''Event handler to "Report Bug" button
        '''
        warning = ReportWarning()
        warning.text = ('Warning. Some web browsers doesn\'t post the full'
                        ' traceback error. \n\nPlease, check if the last line'
                        ' of your report is "End of Traceback". \n\n'
                        'If not, use the "Copy to clipboard" button the get'
                        'the full report and post it manually."')
        warning.bind(on_release=self._do_report)
        warning.open()
        self.warning = warning

    def _do_report(self, *args):
        txt = six.moves.urllib.parse.quote(
            self.txt_traceback.text.encode('utf-8'))
        url = 'https://github.com/kivy/kivy-designer/issues/new?body=' + txt
        webbrowser.open(url)

    def on_close(self, *args):
        '''Event handler to "Close" button
        '''
        App.get_running_app().stop()


class BugReporterApp(App):
    title = "Kivy Designer - Bug reporter"
    traceback = StringProperty('')

    def __init__(self, **kw):
        # self.traceback = traceback
        super(BugReporterApp, self).__init__(**kw)

    def build(self):
        rep = BugReporter()
        template = '''
## Environment Info

%s

## Traceback

```
%s
```

End of Traceback
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
        if isinstance(self.traceback, bytes):
            encoding = sys.getfilesystemencoding()
            if not encoding:
                encoding = sys.stdin.encoding
            if encoding:
                self.traceback = self.traceback.decode(encoding)
        rep.txt_traceback.text = template % (env_info, self.traceback)

        return rep


if __name__ == '__main__':
    BugReporterApp(traceback='Bug example').run()
