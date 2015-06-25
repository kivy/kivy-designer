from kivy import Config
from kivy.uix.codeinput import CodeInput
from kivy.properties import BooleanProperty, ConfigParserProperty
from kivy.utils import get_color_from_hex

from pygments import styles, highlight
from designer.helper_functions import show_alert


class DesignerCodeInput(CodeInput):
    '''A subclass of CodeInput to be used for KivyDesigner.
       It has copy, cut and paste functions, which otherwise are accessible
       only using Keyboard.
       It emits on_show_edit event whenever clicked, this is catched
       to show EditContView;
    '''

    __events__ = ('on_show_edit',)

    clicked = BooleanProperty(False)
    '''If clicked is True, then it confirms that this widget has been clicked.
       The one checking this property, should set it to False.
       :data:`clicked` is a :class:`~kivy.properties.BooleanProperty`
    '''

    def __init__(self, **kwargs):
        super(DesignerCodeInput, self).__init__(**kwargs)
        parser = Config.get_configparser('DesignerSettings')
        if parser:
            parser.add_callback(self.on_codeinput_theme,
                                'global', 'code_input_theme')
            self.style_name = parser.getdefault('global', 'code_input_theme',
                                                'emacs')

    def on_codeinput_theme(self, section, key, value, *args):
        if not value in styles.get_all_styles():
            show_alert("Error", "This theme is not available")
        else:
            self.style_name = value

    def on_style_name(self, *args):
        super(DesignerCodeInput, self).on_style_name(*args)
        self.background_color = get_color_from_hex(self.style.background_color)
        self._trigger_refresh_text()

    def _get_bbcode(self, ntext):
        # override the default method to fix bug with custom themes
        # get bbcoded text for python
        try:
            ntext[0]
            # replace brackets with special chars that aren't highlighted
            # by pygment. can't use &bl; ... cause & is highlighted
            ntext = ntext.replace(u'[', u'\x01').replace(u']', u'\x02')
            ntext = highlight(ntext, self.lexer, self.formatter)
            ntext = ntext.replace(u'\x01', u'&bl;').replace(u'\x02', u'&br;')
            # replace special chars with &bl; and &br;
            ntext = ''.join((u'[color=', str(self.text_color), u']',
                             ntext, u'[/color]'))
            ntext = ntext.replace(u'\n', u'')
            # remove possible extra highlight options
            ntext = ntext.replace(u'[u]', '').replace(u'[/u]', '')

            return ntext
        except IndexError:
            return ''

    def on_show_edit(self, *args):
        pass

    def on_touch_down(self, touch):
        '''Override of CodeInput's on_touch_down event.
           Used to emit on_show_edit
        '''
        if self.collide_point(*touch.pos):
            self.clicked = True
            self.dispatch('on_show_edit')

        return super(DesignerCodeInput, self).on_touch_down(touch)

    def do_copy(self):
        '''Function to do copy operation
        '''

        if self.selection_text == '':
            return

        self._copy(self.selection_text)

    def do_cut(self):
        '''Function to do cut operation
        '''

        if self.selection_text == '':
            return

        self._cut(self.selection_text)

    def do_paste(self):
        '''Function to do paste operation
        '''

        self._paste()

    def do_select_all(self):
        '''Function to select all text
        '''

        self.select_text(0, len(self.text))

    def do_delete(self):
        '''Function to delete selected text
        '''

        if self.selection_text != '':
            self.do_backspace()
