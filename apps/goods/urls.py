from django.urls import path,re_path
from goods.views import GoodsIndexView,GoodsDetailView
urlpatterns = [
    path('index',GoodsIndexView.as_view(),name='index'),
    re_path('detail/?p<goods_id>\d+',GoodsDetailView.as_view(),name='detail'),
]
