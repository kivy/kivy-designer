from functools import partial
from kivy.properties import ObjectProperty, StringProperty, OptionProperty
from kivy.uix.accordion import AccordionItem
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.uix.togglebutton import ToggleButton


class PlaygroundSizeSelector(Button):
    '''Button to open playground size selection view
    '''

    view = ObjectProperty()
    '''This property refers to the
       :class:`~designer.uix.playground_size_selector.PlaygroundSizeView`
       instance.
       :data:`view` is an :class:`~kivy.properties.ObjectProperty`
    '''

    playground = ObjectProperty()
    '''This property holds a reference to the
       :class:`~designer.playground.Playground` instance.
       :data:`playground` is an :class:`~kivy.properties.ObjectProperty`
    '''

    def on_playground(self, *_):
        '''Create a
           :class:`~designer.uix.playground_size_selector.PlaygroundSizeView`
           for the current playground.
        '''
        self.view = PlaygroundSizeView(selected_size=self.playground.size)
        self.view.bind(selected_size=self._update_playground)
        self.view.bind(selected_size_name=self.setter('text'))
        self.text = self.view.selected_size_name

    def _update_playground(self, _, size):
        '''Callback to update the playground size on :data:`selected_size`
           changes
        '''
        if self.playground:
            self.playground.size = size
            if self.playground.root:
                self.playground.root.size = size

    def on_press(self):
        '''Open the
           :class:`~designer.uix.playground_size_selector.PlaygroundSizeView`
        '''
        self.view.size_hint = None, None
        self.view.width = self.get_root_window().width / 2.
        self.view.height = self.get_root_window().height / 2.
        self.view.attach_to = self
        self.view.open()


class PlaygroundSizeView(ModalView):
    '''Dialog for playground size selection
    '''

    accordion = ObjectProperty()
    '''This property holds a reference to the
       :class:`~kivy.uix.accordion.Accordion` inside the dialog.
       :data:`accordion` is an :class:`~kivy.properties.ObjectProperty`
    '''

    selected_size = ObjectProperty()
    '''This property contains the currently selected playground size.
       :data:`selected_size` is an :class:`~kivy.properties.ObjectProperty`
    '''

    selected_size_name = StringProperty('')
    '''This property contains the name associated with :data:`selected_size`.
       :data:`selected_size_name` is a :class:`~kivy.properties.StringProperty`
    '''

    selected_orientation = OptionProperty(
        'landscape', options=('portrait', 'landscape')
    )
    '''This property contains the screen orientation for :data:`selected_size`.
       :data:`selected_orientation` is an
       :class:`~kivy.properties.OptionProperty`
    '''

    default_sizes = (
        ('Desktop - SD', (
            ('Default', (550, 350)),
            ('Small', (800, 600)),
            ('Medium', (1024, 768)),
            ('Large', (1280, 1024)),
            ('XLarge', (1600, 1200))
        )),
        ('Desktop - HD', (
            ('720p', (1280, 720)),
            ('LVDS', (1366, 768)),
            ('1080p', (1920, 1080)),
            ('4K', (3840, 2160)),
            ('4K Cinema', (4096, 2160))
        )),
        ('Generic', (
            ('QVGA', (320, 240)),
            ('WQVGA400', (400, 240)),
            ('WQVGA432', (432, 240)),
            ('HVGA', (480, 320)),
            ('WVGA800', (800, 480)),
            ('WVGA854', (854, 480)),
            ('1024x600', (1024, 600)),
            ('1024x768', (1024, 768)),
            ('1280x768', (1280, 768)),
            ('WXGA', (1280, 800)),
            ('640x480', (640, 480)),
            ('1536x1152', (1536, 1152)),
            ('1920x1152', (1920, 1152)),
            ('1920x1200', (1920, 1200)),
            ('960x640', (960, 640)),
            ('2048x1536', (2048, 1536)),
            ('2560x1536', (2560, 1536)),
            ('2560x1600', (2560, 1600)),
        )),
        ('Android', (
            ('HTC One', (1920, 1080)),
            ('HTC One X', (1920, 720)),
            ('HTC One SV', (800, 480)),
            ('Galaxy S3', (1280, 720)),
            ('Galaxy Note 2', (1280, 720)),
            ('Motorola Droid 2', (854, 480)),
            ('Motorola Xoom', (1280, 800)),
            ('Xperia E', (480, 320)),
            ('Nexus 4', (1280, 768)),
            ('Nexus 7 (2012)', (1280, 800)),
            ('Nexus 7 (2013)', (1920, 1200)),
        )),
        ('iOS', (
            ('iPad 1/2', (1024, 768)),
            ('iPad 3', (2048, 1536)),
            ('iPhone 4', (960, 640)),
            ('iPhone 5', (1136, 640)),
        )),
    )
    '''Ordered map of default selectable sizes.
    '''

    def __init__(self, **kwargs):
        self._buttons = {}

        super(PlaygroundSizeView, self).__init__(**kwargs)

        for title, values in self.default_sizes:
            grid = GridLayout(rows=4)

            def sort_sizes(item):
                return item[1][1] * item[1][0]

            values = sorted(values, key=sort_sizes, reverse=True)
            for name, size in values:
                btn = ToggleButton(text='', markup=True)
                btntext = ('%s\n[color=777777][size=%d]%dx%d[/size][/color]' %
                           (name, btn.font_size * 0.8, size[0], size[1]))
                btn.text = btntext
                btn.bind(on_press=partial(self.set_size, size))
                grid.add_widget(btn)
                self._buttons[name] = btn

            item = AccordionItem(title=title)
            item.add_widget(grid)
            self.accordion.add_widget(item)

        self.accordion.select(self.accordion.children[-1])

        self.update_buttons()

    def find_size(self):
        '''Find the size name and orientation for the current size.
        '''
        orientation = self.check_orientation(self.selected_size)
        check_size = tuple(sorted(self.selected_size, reverse=True)).__eq__
        for _, values in self.default_sizes:
            for name, size in values:
                if check_size(size):
                    return name, size, orientation
        return 'Custom', self.selected_size, orientation

    def check_orientation(self, size):
        '''Determine if the provided size is portrait or landscape.
        '''
        return 'portrait' if size[1] > size[0] else 'landscape'

    def update_buttons(self, size_name=None):
        '''Update the toggle state of the size buttons and open the
           appropriate accordion section.
        '''
        if not size_name:
            size_name = self.find_size()[0]
        for name, btn in list(self._buttons.items()):
            if name == size_name:
                btn.state = 'down'
                self.accordion.select(btn.parent.parent.parent.parent.parent)
            else:
                btn.state = 'normal'

    def on_selected_size(self, *_):
        '''Callback to update properties on changes to :data:`selected_size`.
        '''
        size_info = self.find_size()
        self.selected_size_name = ('%s\n[color=777777](%s, %dx%d)[/color]' %
                                   (size_info[0], size_info[2],
                                    size_info[1][0], size_info[1][1]))
        self.selected_orientation = size_info[2]

        self.update_buttons(size_info[0])

    def update_size(self, size):
        '''Set :data:`selected_size` while taking orientation into account.
        '''
        size = sorted(size, reverse=self.selected_orientation == 'landscape')
        self.selected_size = size

    def set_size(self, size, *_):
        '''Set :data:`selected_size` and close the dialog.
        '''
        self.update_size(size)
        self.dismiss()

    def on_selected_orientation(self, _, value):
        '''Callback to update size on changes to :data:`selected_orientation`.
        '''
        self.update_size(self.selected_size)
