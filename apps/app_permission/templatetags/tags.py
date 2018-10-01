import re, json
from django import template
from django.shortcuts import reverse
# from django.conf import settings as dj_s
from django.utils.safestring import mark_safe
# from django.db.models import Q
from app_permission import settings, models


# ↓static ##############################################################################################################
register = template.Library()

RGX_MENU_ITEM_SUFFIX = re.compile(r'（.+?）$')

MENU_ICONS = {
    '显示主页': 'fa fa-home',
    '客户及项目': 'fa fa-map-marker',
    '存款及用信': 'fa fa-cny',
    '信息共享': 'fa fa-share-alt',
}

def getMenuTree(request):
    menu_tree = request.session.get('menu_tree')
    if menu_tree:
        return json.loads(menu_tree)
    menu_items = request.user.groups.values_list(
        'permissions__mainmenuitem__item__name',
        'permissions__mainmenuitem__item__codename',
        'permissions__mainmenuitem__parent_perm__name',
        # 'permissions__mainmenuitem__parent_perm__codename'
    ).distinct().order_by('permissions__mainmenuitem__display_order')
    menu_struct = {}
    for item in menu_items:
        if item[0] is None:
            continue
        display = RGX_MENU_ITEM_SUFFIX.sub('', item[0], 0)
        try:
            url = reverse(item[1])
        except:
            url = '#'
        parent_display = item[2] and RGX_MENU_ITEM_SUFFIX.sub('', item[2], 0)
        menu_struct[display] = {
            'display': display,
            'url': url,
            'parent_display': parent_display,
            # 'parent_urlname': item[3],
            'children_items': []
        }
    menu_tree = []
    # 算法原理参考《循环实现评论结构》
    for k, v in menu_struct.items():
        parent = v['parent_display']
        if parent:
            menu_struct[parent]['children_items'].append(v)
        else:
            menu_tree.append(v)
    # request.session['menu_tree'] = json.dumps(menu_tree)
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
            icon=MENU_ICONS.get(mt['display'], ''),
            display=mt['display']
        )
        menu_item_lv1 = mt['children_items']
        if menu_item_lv1:
            menu_html += '<ul aria-expanded="false" class="collapse">'
            for mi_lv1 in menu_item_lv1:
                menu_item_lv2 = mi_lv1.get('children_items')
                if menu_item_lv2:
                    menu_html += menu_item_has_child_model.format(href=mi_lv1.get('url', '#'),
                                                                  display=mi_lv1.get('display', 'mi_lv1 None'))
                    menu_html += '<ul aria-expanded="false" class="collapse">'
                    for mi_lv2 in menu_item_lv2:
                        menu_html += menu_item_model.format(href="'" + mi_lv2['url'] + "'",
                                                            display=mi_lv2['display'])
                    menu_html += '</ul>'  # 二级子菜单的闭合标签
                else:
                    menu_html += menu_item_model.format(href="'" + mi_lv1.get('url', '#') + "'",
                                                        display=mi_lv1.get('display', 'mi_lv1 None'))
            menu_html += '</ul>'  # 一级子菜单的闭合标签
        menu_html += '</li>'  # 根菜单项的闭合标签
    menu_html += '</ul></nav></div></aside>'  # 菜单栏的闭合标签
    return mark_safe(menu_html)
# ↑static ##############################################################################################################
# ↓common ##############################################################################################################


@register.simple_tag
def getValue(dic, key):
    return dic.get(key)


@register.simple_tag
def getValueValue(dic, keyDict, key):
    return dic.get(keyDict.get(key))


# ↑common ##############################################################################################################
