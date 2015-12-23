if __name__ == '__main__':
    from designer.app import DesignerApp
    from kivy.resources import resource_add_path
    import os.path
    data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    resource_add_path(data)
    DesignerApp().run()
