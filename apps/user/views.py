from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import View
from django_redis import get_redis_connection
from user.models import User,Address
from goods.models import GoodsSKU
from celery_tasks.tasks import send_register_active_mail
from utils.mixin import LoginRequiredMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re
# Create your views here.


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
        token = token.decode('utf8')
        # 发邮件
        send_register_active_mail.delay(email,username,token)
        # subject = '天天生鲜欢迎信息'
        # message = ''
        # sender = settings.EMAIL_FROM
        # receiver = [email]
        # html_message = '<h1>%s,欢迎您成为天天生鲜的注册会员</h1></br>请点击下面的链接完成激活</br><a href ="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)
        # send_mail(subject, message, sender, receiver, html_message=html_message)
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
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')

class LoginView(View):
    '''登录'''
    def get(self,request):
        '''显示登录页面'''
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request,'login.html',{'username':username,'checked':checked})
    def post(self,request):
        '''登录校验'''

        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验数据
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'数据不完整'})

        # 业务处理
        user = authenticate(username=username,password=password)
        if user is not None:
            # 密码正确

            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request,user)
                # 获取登陆后所要跳转的地址
                # 默认跳转首页
                next_url = request.GET.get('next',reverse('goods:index'))

                # 跳转到首页
                response = redirect(next_url)
                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username',username,max_age=7*3600*24)
                else:
                    response.delete_cookie('username')
                return response

            else:
                return render(request,'login.html',{'errmsg':'用户未激活'})
        else:
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})

        # 返回应答

class LogoutView(View):
    '''退出登录'''
    def get(self,request):
        '''退出登录'''
        # 清除session信息
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))

class UserInfoView(LoginRequiredMixin,View):
    '''用户中心-信息页'''
    def get(self,request):

        # 获取用户的个人信息
        user = request.user
        address = Address.object.get_default_address(user)
        # 获取用户的历史浏览记录
        # from redis import StrictRedis
        # StrictRedis(host='localhost',port='6379',db='5')
        con = get_redis_connection('default')
        history_key = 'history_%d'%user.id
        # 获取用户最新浏览的五条商品id
        sku_id =con.lrange(history_key,0,4)
        # 遍历获取用户浏览的商品信息
        goods_li=[]
        for id in sku_id:
            goods=GoodsSKU.objects.get(id=id)
            goods_li.append(goods)
        # 组织上下文
        context = {
            'page': 'user',
            'address': address,
            'goods_li':goods_li
        }


        return render(request,'user_center_info.html',context)

class UserOrderView(LoginRequiredMixin,View):
    '''用户中心-订单页'''
    def get(self,request):

        # 获取用户的订单信息


        return render(request,'user_center_order.html',{'page':'order'})

class AddressView(LoginRequiredMixin,View):
    '''用户中心-地址页'''
    def get(self,request):

        # 获取用户的默认收货地址
        # 获取登录用户对应的user对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address=Address.object.get_default_address(user)

        return render(request,'user_center_site.html',{'page':'address','address':address})

    def post(self,request):
        '''地址的添加'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})
        # 校验手机号
        if not re.match('^[1](([3][0-9])|([4][5-9])|([5][0-3,5-9])|([6][5,6])|([7][0-8])|([8][0-9])|([9][1,8,9]))[0-9]{8}$',phone):
            return render(request,'user_center_site.html',{'errmsg':'手机号格式不正确'})
        # 业务处理：地址添加
        # 如果用户已有默认收货地址，新添加的不作为默认收货地址，否则作为默认
        # 获取登录用户对应的user对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address=None
        address = Address.object.get_default_address(user)

        if address:
            is_default=False
        else:
            is_default=True
        # 添加地址
        Address.objects.create(user=user,
                               addr=addr,
                               receiver=receiver,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 返回应答,刷新地址页面
        return redirect(reverse('user:address'))