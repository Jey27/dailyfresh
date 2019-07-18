from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings

class FDFSStorage(Storage):
    '''fdfs文件存储类'''
    def __init__(self,client_conf=None,base_url=None):
        '''初始化'''
        if client_conf==None:
            client_conf=settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf
        if base_url==None:
            base_url=settings.FDFS_URL
        self.base_url = base_url
    def _open(self,name,mode='rb'):
        '''打开文件时使用'''
        pass
    def _save(self,name,content):
        '''保存文件时使用'''
        # name：你要上传文件的名字
        # content：包含你要上传文件内容的file对象
        # 创建一个Fdfs_client对象
        client = Fdfs_client(self.client_conf)
        res = client.upload_by_buffer(content.read())
        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件失败')
        filename = res.get('Remote file_id')

        return filename

    def exists(self,name):
        '''django判断文件名是否可用'''
        return False
    def url(self, name):
        '''返回访问文件的url路径'''
        return self.base_url+name


