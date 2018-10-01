import xadmin

from .models import MainMenuItem


class MainMenuItemAdmin:
    list_display = ['item']


xadmin.site.register(MainMenuItem, MainMenuItemAdmin)