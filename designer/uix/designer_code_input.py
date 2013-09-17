from kivy.uix.codeinput import CodeInput
from kivy.core.clipboard import Clipboard
from kivy.properties import BooleanProperty

class DesignerCodeInput(CodeInput):
    '''A subclass of CodeInput to be used for KivyDesigner.
       It has copy, cut and paste functions, which otherwise are accessible
       only using Keyboard.
       It emits on_show_edit event whenever clicked, this is catched to show the
       EditContView;
    '''

    __events__=('on_show_edit',)

    clicked  = BooleanProperty(False)
    '''If clicked is True, then it confirms that this widget has been clicked.
       The one checking this property, should set it to False.
       :data:`clicked` is a :class:`~kivy.properties.BooleanProperty`
    '''

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

        if self.selection_text =='':
            return
        
        self._copy(self.selection_text)
    
    def do_cut(self):
        '''Function to do cut operation
        '''

        if self.selection_text =='':
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
