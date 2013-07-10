from kivy.uix.actionbar import ContextualActionView


class EditContView(ContextualActionView):
    '''EditContView is a ContextualActionView, used to display Edit items:
       Copy, Cut, Paste, Undo, Redo, Select All, Add Custom Widget. It has
       events:
       on_undo, emitted when Undo ActionButton is clicked.
       on_redo, emitted when Redo ActionButton is clicked.
       on_cut, emitted when Cut ActionButton is clicked.
       on_copy, emitted when Copy ActionButton is clicked.
       on_paste, emitted when Paste ActionButton is clicked.
       on_delete, emitted when Delete ActionButton is clicked.
       on_selectall, emitted when Select All ActionButton is clicked.
       on_add_custom, emitted when Add Custom ActionButton is clicked.
    '''

    __events__ = ('on_undo', 'on_redo', 'on_cut', 'on_copy', 'on_paste',
                  'on_delete', 'on_selectall','on_add_custom')
    
    def on_undo(self, *args):
        pass

    def on_redo(self, *args):
        pass

    def on_cut(self, *args):
        pass

    def on_copy(self, *args):
        pass

    def on_paste(self, *args):
        pass

    def on_delete(self, *args):
        pass

    def on_selectall(self, *args):
        pass
        
    def on_add_custom(self, *args):
        pass
        
