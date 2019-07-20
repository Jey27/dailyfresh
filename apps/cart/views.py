from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
# Create your views here.

# ajax发起的请求都在后台，在浏览器上看不到效果，所以不能用mixin
class CartAddView(View):
    '''购物车记录添加'''
    def post(self,request):
        '''购物车记录添加'''
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            # 用户未登录
            return JsonResponse({'res':0,'errmsg':'请先登录'})
        # 接受数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id,count]):
            return JsonResponse({'res':1,'errmsg':'数据不完整'})
        # 校验添加的商品数量
        try:
            count=int(count)
        except Exception as e:
            return JsonResponse({'res':2,'errmsg':'商品数目出错'})
        # 校验商品是否存在
        try:
            res = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res':3,'errmsg':'商品不存在'})

        # 业务处理：添加购物车数据
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # 如果sku_id在hash中不存在，返回None
        cart_count = conn.hget(cart_key,sku_id)
        if cart_count:
            count += cart_count
        # 校验商品库存
        if count>res.stock:
            return JsonResponse({'res':4,'errmsg':'商品库存不足'})
        # 设置hash中对应的值
        conn.hset(cart_key,sku_id,count)
        # 统计用户购物车中商品的总数
        total_count = conn.hlen(cart_key)
        # 返回应答
        return JsonResponse({'res':5,'total_count':total_count,'message':'添加成功'})