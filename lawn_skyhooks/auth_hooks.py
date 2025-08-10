# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA Base Plugin
from lawn_skyhooks import __title__

from . import urls


class ExampleMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            __title__,
            "fas fa-cube fa-fw",
            "lawn_skyhooks:index",
            navactive=["lawn_skyhooks:"],
        )

    def render(self, request):
        if request.user.has_perm("lawn_skyhooks.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return ExampleMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "lawn_skyhooks", r"^lawn_skyhooks/")
