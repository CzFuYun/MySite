import re
from django.urls import resolve
from app_permission import settings, models

# ↓static ##############################################################################################################
class ExtraAuth:
    '''
    该类派生类的作用机制：
    通过传入request及当前用户的queryset来实例化
    并通过请求类型（get,post,put...）映射出应启用的认证函数
    认证函数会返回一个布尔值
    认证函数会被is_allowed方法调用，无需再另外调用
    '''
    def __init__(self, request, user_obj=None):
        self.request = request
        if user_obj:
            self.user_obj = user_obj
        else:
            user_id = request.session.get(settings.USER_ID)
            self.user_obj = models.UserProfile.objects.get(**{settings.USER_ID: user_id})
        self.auth_function = getattr(self, '_' + request.method.lower())

    @property
    def is_allowed(self):
        return self.auth_function()

    def _get(self):
        pass

    def _post(self):
        pass
# ↑static ##############################################################################################################

class viewContribution(ExtraAuth):
    def _get(self):
        return True

    def _post(self):
        user_sdep = self.user_obj.user_id.sub_department.sd_code
        req_dep = self.request.POST.get('dep')
        self.request.req_dep = req_dep
        req_staff = self.request.POST.get('staff')
        self.request.req_staff = req_staff
        if user_sdep in settings.BRANCH_VIEWERS:
            return True
        else:
            user_dep = self.user_obj.user_id.sub_department.superior_id




