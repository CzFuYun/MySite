import xadmin
from xadmin import views

from .models import MainMenuItem, Permission, Role, Role_Perm


class MainMenuItemAdmin:
    list_display = ['item']


class PermissionAdmin:
    list_display = ['description']
    relfield_style = 'fk-ajax'


class RoleAdmin:
    pass


class RolePermAdmin:
    pass


xadmin.site.register(MainMenuItem, MainMenuItemAdmin)
xadmin.site.register(Permission, PermissionAdmin)
xadmin.site.register(Role, RoleAdmin)
xadmin.site.register(Role_Perm, RolePermAdmin)