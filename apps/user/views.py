from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from user.models import User
from django.conf import settings
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re
# Create your views here.
def register(request):
    '''注册视图'''
    if request.method == 'GET':
        # 显示注册页面
        return render(request,'register.html')
    else:
        # 进行注册处理'''
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 判断用户名是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 返回应答
        return redirect(reverse('goods:index'))


def register_handle(request):
    '''进行注册处理'''
    # 接受数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    # 进行数据校验
    if not all([username,password,email]):
        return render(request,'register.html',{'errmsg':'数据不完整'})

    # 校验邮箱
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        return render(request,'register.html',{'errmsg':'邮箱格式不正确'})

    if allow != 'on':
        return render(request,'register.html',{'errmsg':'请同意协议'})
    # 判断用户名是否存在
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    if user:
        return render(request,'register.html',{'errmsg':'用户名已存在'})
    # 进行业务处理：进行注册
    user = User.objects.create_user(username,email,password)
    user.is_active = 0
    user.save()

    # 返回应答
    return redirect(reverse('goods:index'))

class RigisterView(View):
    '''注册'''
    def get(self,request):
        '''显示注册页面'''
        return render(request,'register.html')
    def post(self,request):
        '''进行注册处理'''
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 判断用户名是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件，包含激活链接
        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)

        # 发邮件
        # 返回应答
        return redirect(reverse('goods:index'))

class ActiveView(View):
    '''用户激活'''
    def get(self,request,token):
        '''进行用户激活'''
        # 进行解密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')