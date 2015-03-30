
#: Describe the widgets to show in the toolbox,
#: and anything else needed for the
#: designer. The base is a list, because python dict don't preserve the order.
#: The first field is the name used for Factory.<name>
#: The second field represent a category name

widgets = [
    ('Label', 'base', {'text': 'A label'}),
    ('Button', 'base', {'text': 'A button'}),
    ('CheckBox', 'base'),
    ('Image', 'base'),
    ('Slider', 'base'),
    ('ProgressBar', 'base'),
    ('TextInput', 'base'),
    ('ToggleButton', 'base'),
    ('Switch', 'base'),
    ('Video', 'base'),
    ('ScreenManager', 'base'),
    ('Screen', 'base'),
    ('Carousel', 'base'),
    ('TabbedPanel', 'base'),
    ('GridLayout', 'layout', {'cols': 2}),
    ('BoxLayout', 'layout'),
    ('AnchorLayout', 'layout'),
    ('StackLayout', 'layout'),
    ('FileChooserListView', 'complex'),
    ('FileChooserIconView', 'complex'),
    ('Popup', 'complex'),
    ('Spinner', 'complex'),
    ('VideoPlayer', 'complex'),
    ('ActionButton', 'complex'),
    ('ActionPrevious', 'complex'),
    ('ScrollView', 'behavior'),
    # ('VKeybord', 'complex'),
    # ('Scatter', 'behavior'),
    # ('StencilView', 'behavior'),
]
