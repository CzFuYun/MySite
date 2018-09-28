from django.db import models
from django.contrib.auth.models import AbstractUser, Group

from app_permission import settings

# ↓static ##############################################################################################################
class UserProfile(AbstractUser):
    user_id = models.OneToOneField(
        to=settings.USER_RESOURCE_MODEL,
        to_field=settings.USER_ID_RESOURCE_FIELD,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    roles = models.ManyToManyField('Role')      # 一个用户可能拥有多重角色


class Permission(models.Model):
    widget_type_choices = (
        (0, None),

    )
    description = models.CharField(max_length=64, db_index=True)
    url_name = models.CharField(max_length=64, blank=True, null=True)
    # ↑可以为空，是因为某些菜单节点没有url路由规则。
    # 例如主菜单栏上的大部分根条目，点击后并不产生url路由，但这些根条目也应该是权限的一部分
    # 因为某些用户可能无权看到特定的根条目
    widget_type = models.SmallIntegerField(choices=widget_type_choices, default=0)
    display_caption = models.CharField(max_length=32, null=True, blank=True)        # 在Menu或前端其他区域展示时的名称

    def __str__(self):
        return self.description


class MainMenuItem(models.Model):
    item = models.OneToOneField('Permission', on_delete=models.CASCADE)
    parent_perm = models.ForeignKey('Permission', null=True, on_delete=models.CASCADE, related_name='parent_item')
    display_order = models.SmallIntegerField(null=True, blank=True)      # 在菜单栏的先后顺序，根条目必填

    def __str__(self):
        caption_list = [self.item.display_caption, ]
        p = self.parent_perm
        while p:
            caption_list.insert(0, p.item.display_caption)
            p = p.parent_perm
        return '-'.join(caption_list)


class Role(models.Model):
    caption = models.CharField(max_length=32, unique=True)
    permissions = models.ManyToManyField('Permission', through='Role_Perm')

    def __str__(self):
        return self.caption


class Role_Perm(models.Model):
    role_id = models.ForeignKey('Role', to_field='id', on_delete=models.CASCADE)
    permission_id = models.ForeignKey('Permission', to_field='id', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '角色与权限'
        verbose_name_plural = verbose_name
        unique_together = ['role_id', 'permission_id']
        ordering = ['role_id', 'permission_id']

    def __str__(self):
        return self.role_id.caption + '——' + self.permission_id.description
# ↑static ##############################################################################################################


