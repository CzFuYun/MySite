from django.conf.urls import url
import xadmin


urlpatterns = [
    url(r'', xadmin.site.urls),
]