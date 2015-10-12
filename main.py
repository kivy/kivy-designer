if __name__ == '__main__':
    from designer.app import DesignerApp
    from kivy.resources import resource_add_path
    import os.path
    resource_add_path(os.path.join(os.path.dirname(__file__), 'data'))
    DesignerApp().run()
