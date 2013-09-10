from kivy.uix.actionbar import ActionGroup, ActionButton, ActionPrevious, ActionItem
from designer.uix.contextual import MenuButton, ContextMenu, ContextSubMenu

class DesignerActionPrevious(ActionPrevious):
    pass

class DesignerActionSubMenu(ContextSubMenu, ActionItem):
    pass
    
class DesignerActionGroup(ActionGroup):
    pass

class DesignerActionButton(ActionItem, MenuButton):
    pass