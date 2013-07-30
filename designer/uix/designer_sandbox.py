from kivy.uix.sandbox import Sandbox

class DesignerSandbox(Sandbox):
    '''DesignerSandbox is subclass of :class:`~kivy.uix.sandbox.Sandbox`
       for use with Kivy Designer. It emits on_getting_exeption event
       when code running in it will raise some exception.
    '''

    __events__ = ('on_getting_exception',)
    
    def __exit__(self, _type, value, tb):
        self._context.pop()
        #print 'EXITING THE SANDBOX', (self, _type, value, tb)
        if _type is not None:
            return self.on_exception(value, tb=tb)

    def on_exception(self, exception, tb=None):
        self.exception = exception
        self.tb = tb
        self.dispatch('on_getting_exception')
        return super(DesignerSandbox, self).on_exception(exception, tb)
    
    def on_getting_exception(self, *args):
        pass