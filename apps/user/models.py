from db.base_model import BaseModel
from django.db import models
from django.contrib.auth.models import AbstractUser
class User(AbstractUser,BaseModel):
    '''用户模型类'''

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
class AddressManager(models.Manager):#应用技术：模型管理类（缩小搜索集作用，extra增加增删改查的功能）
    '''替换父类object的默认模型管理器类models.Manager'''
    def get_default_address(self,user):#user会自动查询数据库forigenkey查到，或views中django定义request获取到该user板块全部数据
        try:
            address = self.get(user=user,is_default=True)
            #最开始address = Address.objects.get() ==>self.get()
            """
            已知Address.objects==AddressManager()如下class定义
            所以Address.objects.get() == AddressManager() == self(即是自身的类对象)
            """
            '''Django定义：self.model==Address'''
        except self.model.DoesNotExist:#Address.DoesNotExit:
            address = None
        return address
class Address(BaseModel):
    user = models.ForeignKey('User',verbose_name='所属账户',on_delete=models.CASCADE)
    receiver = models.CharField(max_length=20,verbose_name='收件人')
    addr = models.CharField(max_length=120,verbose_name='详细地址')
    zip_code = models.IntegerField(verbose_name='邮编',null=True)
    phone = models.CharField(max_length=11,verbose_name='手机')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')
    objects = AddressManager()
    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
