from kivy.app import App
from kivy.properties import ObjectProperty, Clock, partial
from kivy.uix.actionbar import ContextualActionView
from kivy.modules import screen
import webbrowser
from designer.uix.designer_action_items import DesignerActionProfileCheck


class ModulesContView(ContextualActionView):

    mod_screen = ObjectProperty(None)

    __events__ = ('on_module', )

    def on_module(self, *args, **kwargs):
        '''Dispatch the selected module
        '''
        self.parent.on_previous(self)

    def on_screen(self, *args):
        '''Screen module selected, shows ModScreenContView menu
        '''
        if self.mod_screen is None:
            self.mod_screen = ModScreenContView()
            self.mod_screen.bind(on_run=self.on_screen_module)
        self.parent.add_widget(self.mod_screen)

    def on_screen_module(self, *args, **kwargs):
        '''when running from screen module
        '''
        self.mod_screen.parent.on_previous(self.mod_screen)
        self.dispatch('on_module', *args, **kwargs)

    def on_webdebugger(self, *args):
        '''when running from webdebugger'''
        self.dispatch('on_module', mod='webdebugger', data=[])
        Clock.schedule_once(partial(webbrowser.open,
                                    'http://localhost:5000/'), 5)


class ModScreenContView(ContextualActionView):

    __events__ = ('on_run', )

    designer = ObjectProperty(None)
    '''Instance of Desiger
    '''

    def __init__(self, **kwargs):
        super(ModScreenContView, self).__init__(**kwargs)

        # populate emulation devices
        devices = self.ids.module_screen_device

        self.designer = App.get_running_app().root
        config = self.designer.designer_settings.config_parser

        # load the default values
        saved_device = config.getdefault('internal', 'mod_screen_device', '')
        saved_orientation = config.getdefault('internal',
                                              'mod_screen_orientation', '')
        saved_scale = config.getdefault('internal', 'mod_screen_scale', '')

        first = True
        first_btn = None
        for device in sorted(screen.devices):
            btn = DesignerActionProfileCheck(group='mod_screen_device',
                            allow_no_selection=False, config_key=device)
            btn.text = screen.devices[device][0]
            btn.bind(on_active=self.on_module_settings)

            if first:
                btn.checkbox_active = True
                first_btn = btn
                first = False
            else:
                if device == saved_device:
                    first_btn.checkbox.active = False
                    btn.checkbox_active = True
                else:
                    btn.checkbox_active = False

            devices.add_widget(btn)
        for orientation in self.ids.module_screen_orientation.list_action_item:
            if orientation.config_key == saved_orientation:
                orientation.checkbox_active = True

        for scale in self.ids.module_screen_scale.list_action_item:
            if scale.config_key == saved_scale:
                scale.checkbox_active = True

    def on_run_press(self, *args):
        '''Run button pressed. Analyze settings and dispatch ModulesContView
                on run
        '''
        device = None
        orientation = None
        scale = None

        for d in self.ids.module_screen_device.list_action_item:
            if d.checkbox.active:
                device = d.config_key
                break

        for o in self.ids.module_screen_orientation.list_action_item:
            if o.checkbox.active:
                orientation = o.config_key
                break

        for s in self.ids.module_screen_scale.list_action_item:
            if s.checkbox.active:
                scale = s.config_key
                break

        parameter = '%s,%s,scale=%s' % (device, orientation, scale)

        self.dispatch('on_run', mod='screen', data=parameter)

    def on_run(self, *args, **kwargs):
        '''Event handler for on_run
        '''
        pass

    def on_module_settings(self, instance, *args):
        '''Event handle to save Screen Module settings when a different
        option is selected
        '''
        if instance.checkbox.active:
            self.designer.designer_settings.config_parser.set(
                'internal',
                instance.group,
                instance.config_key
            )
            self.designer.designer_settings.config_parser.write()
