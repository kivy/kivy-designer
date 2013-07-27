from kivy.uix.sandbox import Sandbox

class DesignerSandbox(Sandbox):
    '''DesignerSandbox is subclass of :class:`~kivy.uix.sandbox.Sandbox`
       for use with Kivy Designer. It emits on_getting_exeption event
       when code running in it will raise some exception.
    '''

    __events__ = ('on_getting_exception',)

    def on_exception(self, exception, tb=None):
        self.exception = exception
        self.tb = tb
        self.dispatch('on_getting_exception')
        return super(DesignerSandbox, self).on_exception(exception, tb)
    
    def on_getting_exception(self, *args):
        pass