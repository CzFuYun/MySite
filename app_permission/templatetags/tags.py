import re, json
from django import template
from django.shortcuts import reverse
# from django.conf import settings as dj_s
from django.utils.safestring import mark_safe
# from django.db.models import Q
from app_permission import settings, models


# ↓static ##############################################################################################################
register = template.Library()

def getMenuTree(request):
    menu_tree = request.session.get('menu_tree')
    if menu_tree:
        return json.loads(menu_tree)
    user_id = request.session[settings.USER_ID]
    user_obj = models.UserProfile.objects.get(**{settings.USER_ID: user_id})
    # 取到用户角色的全部权限
    user_perms = user_obj.roles.values_list(
        settings.ROLE_PERMISSIONS + '__' + 'id',
        settings.ROLE_PERMISSIONS + '__' + settings.PERMISSION_DESCRIPTION,
        settings.ROLE_PERMISSIONS + '__' + settings.PERMISSION_URL_NAME,
        settings.ROLE_PERMISSIONS + '__' + settings.PERMISSION_DISPLAY_CAPTION
    ).distinct().order_by('permissions__mainmenuitem__display_order')
    user_perms_list = []
    for up in user_perms:
        user_perms_list.append(
            {
                'perm_id': up[0],
                settings.PERMISSION_DESCRIPTION: up[1],
                settings.PERMISSION_URL_NAME: up[2],
                settings.PERMISSION_DISPLAY_CAPTION: up[3],
            }
        )
    # print(user_perms_list)
    menu_items_dict = {}
    for upl in user_perms_list:
        menu_item = models.MainMenuItem.objects.filter(**{
            settings.MENU_ITEM + '__' + settings.PERMISSION_DESCRIPTION: upl[settings.PERMISSION_DESCRIPTION]
        })
        try:
            _url = reverse(upl[settings.PERMISSION_URL_NAME])
        except:
            _url = '#'
        if menu_item:
            upl['url'] = _url
            upl['parent'] = menu_item[0].parent_perm_id
            upl['children'] = []
            menu_items_dict[upl['perm_id']] = upl
    # print(menu_items_dict)        #{1: {'id': 1, 'description': '全行存款概览', 'url_name': 'viewOverViewBranch', 'display_caption': '全行存款概览', 'parent': None, 'children': []}, 2: {'id': 2, 'description': 'yyy', 'url_name': 'ajaxOverViewBranch', 'display_caption': None, 'parent': 1, 'children': []}, 3: {'id': 3, 'description': 'xxx', 'url_name': 'ajaxAnnotateDeposit', 'display_caption': None, 'parent': 1, 'children': []}}
    menu_tree = []
    # 算法原理参考《循环实现评论结构》
    for k, v in menu_items_dict.items():
        p_id = v['parent']
        if p_id:
            menu_items_dict[p_id]['children'].append(v)
        else:
            menu_tree.append(v)
    # print(menu_tree)
    # [{'id': 1, 'description': '全行存款概览', 'url_name': 'viewOverViewBranch', 'display_caption': '全行存款概览', 'parent': None, 'children': [{'id': 2, 'description': 'yyy', 'url_name': 'ajaxOverViewBranch', 'display_caption': None, 'parent': 1, 'children': []}, {'id': 3, 'description': 'xxx', 'url_name': 'ajaxAnnotateDeposit', 'display_caption': None, 'parent': 1, 'children': []}]}]
    request.session['menu_tree'] = json.dumps(menu_tree)
    return menu_tree

@register.simple_tag
def buildMenu(request):
    menu_tree = getMenuTree(request)
    menu_html = '''
        <aside class="left-sidebar">
            <div class="scroll-sidebar">
                <nav class="sidebar-nav active">
                    <ul id="sidebarnav" class="in">
        '''
    # ↓菜单栏上的“根菜单”项
    menu_bar_item_model = '''
        <li root_item>
            <a class="has-arrow waves-effect waves-dark" href="{href}" aria-expanded="false">
                <i class="{icon}"></i>
                <span class="hide-menu">{display}</span>
            </a>
        '''
    menu_item_model = '<li><a href="javascript:clickMenu({href});">{display}</a></li>'
    menu_item_has_child_model = '<li><a class="has-arrow" href="javascript:clickMenu({href});">{display}</a></li>'
    for mt in menu_tree:
        menu_html += menu_bar_item_model.format(
            href=mt['url'],
            icon=settings.MENU_ICONS.get(mt[settings.PERMISSION_DESCRIPTION], ''),
            display=mt[settings.PERMISSION_DISPLAY_CAPTION]
        )
        menu_item_lv1 = mt['children']
        if menu_item_lv1:
            menu_html += '<ul aria-expanded="false" class="collapse">'
            for mi_lv1 in menu_item_lv1:
                menu_item_lv2 = mi_lv1['children']
                if menu_item_lv2:
                    menu_html += menu_item_has_child_model.format(href=mi_lv1['url'],
                                                                  display=mi_lv1[settings.PERMISSION_DISPLAY_CAPTION])
                    menu_html += '<ul aria-expanded="false" class="collapse">'
                    for mi_lv2 in menu_item_lv2:
                        menu_html += menu_item_model.format(href="'" + mi_lv2['url'] + "'",
                                                            display=mi_lv2[settings.PERMISSION_DISPLAY_CAPTION])
                    menu_html += '</ul>'  # 二级子菜单的闭合标签
                else:
                    menu_html += menu_item_model.format(href="'" + mi_lv1['url'] + "'",
                                                        display=mi_lv1[settings.PERMISSION_DISPLAY_CAPTION])
            menu_html += '</ul>'  # 一级子菜单的闭合标签
        menu_html += '</li>'  # 根菜单项的闭合标签
    menu_html += '</ul></nav></div></aside>'  # 菜单栏的闭合标签
    return mark_safe(menu_html)
# ↑static ##############################################################################################################

@register.simple_tag
def getValue(dic, key):
    return dic.get(key)\


@register.simple_tag
def getValueValue(dic, keyDict, key):
    return dic.get(keyDict.get(key))