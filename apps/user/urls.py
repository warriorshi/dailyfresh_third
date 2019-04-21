from django.urls import path,re_path
from user.views import RegisterView,ActiveView,LoginView,LogoutView,UserCenterInfoView,UserAddressView,UserCenterOrderView
from django.conf.urls import url

urlpatterns = [
    path('register',RegisterView.as_view(),name='register'),
    re_path('active/(?P<token>.*)',ActiveView.as_view(),name='activelineto'),
    path('login',LoginView.as_view(),name='login'),
    path('logout',LogoutView.as_view(),name='logout'),
    path('usercenter',UserCenterInfoView.as_view(),name='usercenter'),
    path('usercenter_site',UserAddressView.as_view(),name='usercenter_site'),
    path('usercenter_order',UserCenterOrderView.as_view(),name='usercenter_order'),
    # url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),
]
