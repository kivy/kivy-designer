from designer.app import DesignerApp
from designer.helper_functions import get_fs_encoding
from kivy.resources import resource_add_path
import os.path


if __name__ == '__main__':
    data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if isinstance(data, bytes):
        data = data.decode(get_fs_encoding())
    resource_add_path(data)
    DesignerApp().run()
