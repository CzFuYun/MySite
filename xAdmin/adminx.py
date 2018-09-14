import xadmin
from xadmin import views


class BaseSetting:
    enable_themes = True
    use_bootswatch = True


class GlobalSetting:
    site_title = "自助填报系统"
    site_footer = "华夏银行常州分行公司业务部"


xadmin.site.register(views.CommAdminView, GlobalSetting)
xadmin.site.register(views.BaseAdminView, BaseSetting)