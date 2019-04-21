from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/',admin.site.urls),
    path('user/',include(('user.urls','user'),namespace='user')),
    path('goods/',include(('goods.urls','goods'),namespace='goods')),
    path('tinymce/',include('tinymce.urls')),

]
