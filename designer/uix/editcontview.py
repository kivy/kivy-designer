from kivy.uix.actionbar import ContextualActionView


class EditContView(ContextualActionView):

    __events__ = ('on_undo', 'on_redo', 'on_cut', 'on_copy', 'on_paste',
                  'on_delete', 'on_selectall',)
    
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
    
    
