#相当于完成从admin管理界面上传到异地机器的fdfs的storage过程
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
class FDFSStorage(Storage):
    '''fast dfs文件存储类'''
    def __init__(self, client_conf=None, base_url=None):
        '''初始化'''
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

    def _open(self,name,mode='rb'):
        '''打开文件时使用'''
        pass
    def _save(self,name,content):#name :选择上传文件的名字#content:包含你上传文件内容的File对象
        '''保存文件时使用'''
        # name:你选择上传文件的名字 test.jpg
        # content:包含你上传文件内容的File对象
        #创建一个Fdfs_client对象
        client = Fdfs_client(self.client_conf)
        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': local_file_name,
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        ''''''
        #上传文件到fast dfs系统中
        res = client.upload_by_buffer(content.read())

        #获取返回的文件ID
        filename = res.get('Remote file_id')
        return filename
    def exists(self, name):
        '''Django判断文件名是否可用'''
        return False    #可用，没有这个文件名/id
    def url(self,name):
        '''Django返回访问文件的url路径,并最终被html取得到 (nginx端口号8888)'''
        # return 'http://192.168.211.200:8888/'+name
        return self.base_url+name
