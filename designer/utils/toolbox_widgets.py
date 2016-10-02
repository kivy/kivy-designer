#: Describe the widgets to show in the toolbox,
#: and anything else needed for the
#: designer. The base is a list, because python dict don't preserve the order.
#: The first field is the name used for Factory.<name>
#: The second field represent a category name
#: The third field represents initial widget values
#: The fourth field are extra parameters used to display the widget while dragging
toolbox_widgets = [
    ('Button', 'base', {'text': 'Button'}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('Carousel', 'base'),
    ('CheckBox', 'base', {'active': True}, {'size_hint': (None, None), 'size': ('50sp', '50sp')}),
    ('Image', 'base', {'source': 'data/logo/kivy-icon-64.png'}, {'size_hint': (None, None), 'size': (64, 64)}),
    ('Label', 'base', {'text': 'Label'}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('ProgressBar', 'base', {}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('Screen', 'base'),
    ('ScreenManager', 'base'),
    ('Slider', 'base', {}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('Switch', 'base', {'active': True}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('TextInput', 'base', {'text': 'Text Content'}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('ToggleButton', 'base', {'text': 'Toggle Button'}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('Video', 'base'),

    ('AnchorLayout', 'layout'),
    ('BoxLayout', 'layout'),
    ('FloatLayout', 'layout'),
    ('GridLayout', 'layout', {'cols': 2}),
    ('PageLayout', 'layout'),
    ('RelativeLayout', 'layout'),
    ('ScatterLayout', 'layout'),
    ('StackLayout', 'layout'),

    ('ActionButton', 'complex'),
    ('ActionPrevious', 'complex', {}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('Bubble', 'complex', {}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('DropDown', 'complex'),
    ('FileChooserListView', 'complex', {}, {'size_hint': (None, None), 'size': ('200sp', '160sp')}),
    ('FileChooserIconView', 'complex', {}, {'size_hint': (None, None), 'size': ('200sp', '160sp')}),
    ('ListView', 'complex', {'item_strings': ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']}, {'size_hint': (None, None), 'size': ('100sp', '140sp')}),
    ('Popup', 'complex'),
    ('Spinner', 'complex', {'text': 'Spinner'}, {'size_hint': (None, None), 'size': ('150sp', '40sp')}),
    ('TabbedPanel', 'complex'),
    ('VideoPlayer', 'complex', {}, {'size_hint': (None, None), 'size': ('200sp', '150sp')}),

    ('ScrollView', 'behavior'),
    ('Scatter', 'behavior'),
    ('StencilView', 'behavior'),
]

