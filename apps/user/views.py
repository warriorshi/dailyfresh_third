from django.http import HttpResponse
#可以从django.shortcuts中导入render()来渲染页面.html,
# 直接代替这个HttpResponse(只是回传一些简单的东西),
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import View
import re
from user.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate,login,logout
from goods.models import GoodsSKU
from user.models import Address
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
import time


class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')
    def post(self,request):
        #接收数据
        username = request.POST.get('user_name')#是从浏览器界面提交，不是数据库所以方法是request.POST而不是通过models.objects的方式
        password = request.POST.get('pwd')
        cwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        #校验数据
        if not all([username,password,cwd,email,allow]):
            return render(request,'register.html',{'errmsg':'信息不全'})
        if not re.match(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$',email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '该用户名已存在'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请阅读协议，并勾选'})

        #业务处理
        user = User.objects.create_user(username,email,password)
        user.is_active = 0
        user.save()

        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()

        #涉及celery
        send_register_active_email.delay(email,username,token)
        return redirect(reverse('goods:index'))


class ActiveView(View):
    def get(self,request,token):
        #接收数据(根据链接，这里的是token而不直接是user_id)
        serializer = Serializer(settings.SECRET_KEY,3600)
        try:
            # 业务处理
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('您的链接已过期，请重新注册')
class LoginView(View):
    def get(self,request):
        #接收数据：判断是否接收数据
        if 'username' in request.COOKIES:#看浏览器设置的cookie里username字段是否被删除，cookies因为是浏览器中的所以是携带在request中的
            username = request.COOKIES.get('username')
            # password = request.COOKIES.get('pwd')
            checked = 'checked'#左边为变量，右边为状态值。这里是设置checked值不是获取
        else:
            username =''
            checked = ''
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):#登陆
        #接收参数，从request.post中获取
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        #校验参数
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'信息不全'})
        user = authenticate(username= username,password=password)

        if user:#if user is not None:
            if user.is_active:
                login(request,user)
                next_url = request.GET.get('next',reverse('goods:index'))#GET.get()获取next后边的url值。这是在访问依赖于用户的url时会执行的程序，设置的默认值为后边的reverse()
                response = redirect(next_url)
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username',username,max_age=7*24*3600)
                    checked = 'checked'
                else:
                    response.delete_cookie('username',username)
                return response
            else:
                return render(request,'login.html',{'errmsg':'请激活用户'})
        else:
            return render(request,'login.html',{'errmsg':'请注册用户'})

        #返回应答

class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect(reverse('goods:index'))
class UserCenterInfoView(LoginRequiredMixin,View):
    def get(self,request):
        #接收数据
        user = request.user
        user_id = user.id
        address = Address.objects.get_default_address(user)
            #获取历史浏览记录
        con = get_redis_connection('default')#cache里的default,用的是django-redis组件而不直接用连redis了
        #直接连redis:
        # from redis import StrictRedis
        # sr = StrictRedis(host='192.168.211.220', port='6379', db=2),同义上句
        history_key = 'history%d'%user_id
        sku_ids = con.lrange(history_key,0,4)
        # 错误：goods_li = GoodsSKU.objects.filter(id__in=sku_ids)#不按照浏览/查询顺序返回，所以还要做如下操作给它顺序
        # 实验：select * from df_goods_sku where id in (2,3,1);等效，查询结果是还是1,2,3的顺序
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        context = {'page':'user',
                   'goods_li':goods_li,
                   'address':address
        }
        return render(request,'user_center_info.html',context)


class UserCenterOrderView(LoginRequiredMixin,View):
    def get(self,request):

        return render(request,'user_center_order.html',{'page': 'order'})
    def post(self,request):
        pass
class UserAddressView(LoginRequiredMixin,View):
    def get(self,request):
        user = request.user
        address = Address.objects.get_default_address(user)#默认收货地址
        return render(request,'user_center_site.html',{'page': 'site','address':address})
    def post(self,request):
        #接收参数
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        #校验
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site',{'errmsg':'信息填写不全'})
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
            return render(request,'user_center_site',{'errmsg':'电话号码有误'})
        user = request.user
        address = Address.objects.get_default_address(user)
        if address:#如果有默认地址
            is_default = False
        else:
            is_default = True
        # context = {'user':user,'receiver':receiver,'addr':addr,'phone':phone,'zip_code':zip_code,'is_default':is_default}
        # return render(request,'user_center_site.html',context)
        #业务处理：在数据库中创建该Address对象
        Address.objects.create(user=user,receiver=receiver,addr=addr,phone=phone,zip_code=zip_code,is_default=is_default)
        return redirect(reverse('user:usercenter_site'))
