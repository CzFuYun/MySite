# ↓static ##############################################################################################################
# PERMITTED_URLS = 'permitted_urls'
# MENU_ALL_ITEMS = 'menu_all_items'
# MENU_PERMITTED_ITEMS = 'menu_permitted_items'

# 用户表中，用户id的字段名：
# USER_ID = 'username'
# 用户表中，密码的字段名：
# PASSWORD = 'password'
# Permission表的表名
# PERMISSION_TABLE = 'permission'
# Permission表中权限描述的字段名称
# PERMISSION_DESCRIPTION = 'name'
# Permission表中权限的url别名的字段名称：
# PERMISSION_URL_NAME = 'url_name'
# Permission表中权限显示名的字段名称：
# PERMISSION_DISPLAY_CAPTION = 'name'
# Role表中，所具备的权限，字段名：
# ROLE_PERMISSIONS = 'permissions'
# MainMenuItem表中，item字段名：
# MENU_ITEM = 'item'
# MainMenuItem表中，parent字段名：
# MENU_ITEM_PARENT = 'parent_perm'

# session有效期（秒）：
SESSION_AGE = 16 * 3600
# ↑static ##############################################################################################################



# ↓dynamic #############################################################################################################
# # 静态文件夹的名称：
# STATIC_FOLDER_NAME = 'static'
#

# 用户来源：
USER_RESOURCE_MODEL = 'root_db.Staff'
# 用户id字段来源：
USER_ID_RESOURCE_FIELD = 'staff_id'


# 登录的url name:
LOGIN_URL_NAME = 'login'
# 登录页面的名称：
LOGIN_PAGE = 'login.html'
# 主页的url name：
HOME_URL_NAME = 'home'
# 主页的名称：
HOME_PAGE = 'home.html'



# url参数中细分部门的参数名
SUB_DEPARTMENT = 'sdep'
# url参数中部门的参数名
DEPARTMENT = 'dep'

BRANCH_VIEWERS = ['JGBS-0', 'JGBS-12', ]

# ↑dynamic ##############################################################################################################