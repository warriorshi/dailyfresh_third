from django.conf.urls import url,include
from django.conf.urls import url, include
from django.urls import path
urlpatterns = [
    url('^admin/', admin.site.urls),
    url(r'^tinymce/',include('tinymce.urls')),#富文本编辑器
]

