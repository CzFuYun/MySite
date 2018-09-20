import xadmin
from xadmin import views
from xadmin.plugins.auth import UserAdmin

from app_permission import models as p_m
from app_customer_repository import models as cr_m


class BaseSetting:
    # enable_themes = True
    # use_bootswatch = True
    pass


class GlobalSetting:
    site_title = "自助填报系统"
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


class ProjectAdmin:
    list_display = ('customer', 'staff', 'tmp_close_date', 'close_reason', )


class PretrialDocumentAdmin:
    list_display = ('customer_name', 'department', 'accept_date', 'reason', 'net_total', 'agree_net', 'result', 'meeting', )
    list_per_page = 20
    list_filter = ('meeting__caption', 'meeting__meeting_date', 'reason', )
    # list_export_fields = ('', '',)


class PretrialMeetingAdmin:
    list_display = ('caption', 'meeting_date', )
    list_per_page = 20


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSetting)
xadmin.site.register(cr_m.ProjectRepository, ProjectAdmin)
xadmin.site.register(cr_m.PretrialDocument, PretrialDocumentAdmin)
xadmin.site.register(cr_m.PretrialMeeting, PretrialMeetingAdmin)