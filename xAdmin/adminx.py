import xadmin
from xadmin import views


class BaseSetting:
    # enable_themes = True
    # use_bootswatch = True
    pass


class GlobalSetting:
    site_title = "信息共享系统"
    site_footer = "华夏银行常州分行公司业务部"
    menu_style = "accordion"


# class UserProfileAdmin:
#     list_display = ('user_id', 'password', 'roles', )
#     readonly_fields = ('password', )
#     # style_fields = {'roles': 'checkbox-inline', }     # 报错
#     list_per_page = 10
#     show_detail_fields = ('user_id', )
#     refresh_times = (3, 5)
#     list_export = ('xls', 'xml', 'csv', 'json', )
#     list_export_fields = ('user_id', 'roles', )
#     list_filter = ('user_id', )
#     # search_fields = ('user_id', )     # 报错
#
#     def get_readonly_fields(self):
#         if self.user.is_superuser:
#             self.readonly_fields = []
#         return self.readonly_fields
#
# xadmin.site.register(p_m.UserProfile, UserProfileAdmin)
# class UserProfileAdmin(UserAdmin):
#     pass
#
# xadmin.site.register(p_m.UserProfile, UserProfileAdmin)





xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSetting)
