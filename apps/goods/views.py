from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner,GoodsSKU
from django_redis import get_redis_connection
from django.contrib.auth import authenticate
# Create your views here.
#首页视图/goods/index
class GoodsIndexView(View):
   def get(self,request):
      # 接收数据
      types = GoodsType.objects.all()
      goods_banners = IndexGoodsBanner.objects.all().order_by('index')
      promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

      for type in types:#type作为GoodsType的实例并没有具体的跟商品分类展示模型相关的属性集，在这里加上，并使之通过filter反向联系IndexTypeGoodsBanner集合再反向外键反向联系上sku。
         title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by('index')
         image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')

         type.title_banners = title_banners
         type.image_banners = image_banners

      cart_count = 1
      context = {
         'types':types,
         'goods_banners':goods_banners,
         'promotion_banners':promotion_banners,
         'cart_count':cart_count
      }
      return render(request,'index.html',context)
#商品详情页/goods/detail
class GoodsDetailView(View):
   def get(self,request,goods_id):
      #接收数据
      types = GoodsType.objects.all()
      sku = GoodsSKU.objects.get(id=goods_id)
      #校验数据

      #业务处理：购物车更新，新品推荐
         #购物车更新,涉及到redis数据库中的cart
      if authenticate(request):
         cart_count = 0
      else:
         con = get_redis_connection('default')
         cart_key = 'cart_%d' % user_id #使用user_id在cart后边保证这个cart的唯一性，不会命名错，且是与user互相对应的
         cart_count = len(con.history_key)
         #新品推荐
         sku.lren().orderby(-createtime)[:2]
