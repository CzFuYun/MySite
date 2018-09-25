import xadmin
from xadmin import views

from .models import MainMenuItem, Permission, Role


class MainMenuItemAdmin:
    list_display = ['item']


class PermissionAdmin:
    list_display = ['description']


class RoleAdmin:
    pass


xadmin.site.register(MainMenuItem, MainMenuItemAdmin)
xadmin.site.register(Permission, PermissionAdmin)
xadmin.site.register(Role, RoleAdmin)