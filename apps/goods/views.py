from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner,GoodsSKU
from order.models import OrderGoods
from django_redis import get_redis_connection
# Create your views here.

class IndexView(View):
    def get(self,request):
        '''首页'''
        #  获取商品种类信息
        types = GoodsType.objects.all()
        # 获取首页商品轮播信息
        goods_banners = IndexGoodsBanner.objects.all().order_by('index')

        # 获取首页促销商品信息
        promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

        # 获取首页分类商品展示信息
        # type_goods_banners = IndexTypeGoodsBanner.objects.all()
        for type in types:
            title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by('index')
            image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')
            # 动态的给type增加属性，分别保存首页图片展示和首页标题展示
            type.title_banners = title_banners
            type.image_banners = image_banners
        # 获取购物车商品数目
        cart_count = 0
        user = request.user
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context={
            'types':types,
            'goods_banners':goods_banners,
            'promotion_banners':promotion_banners,
            'cart_count':cart_count
        }

        return render(request,'index.html',context)

class DetailView(View):
    '''商品详情页'''
    def get(self,request,goods_id):
        # 获取商品信息
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]
        # 获取同一个spu的商品信息
        same_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)
        # 获取购物车商品数目
        cart_count = 0
        user = request.user
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
            # 添加用户历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d'%user.id
            # 移除已存在的历史记录
            conn.lrem(history_key,0,goods_id)
            # 吧goodsid左侧插入
            conn.lpush(history_key,goods_id)
            # 只保存用户最新浏览的五条信息
            conn.ltrim(history_key,0,4)
        # 组织上下文
        context = {
            'sku':sku,
            'types':types,
            'sku_orders':sku_orders,
            'new_skus':new_skus,
            'cart_count':cart_count,
            'same_skus':same_skus,
        }
        return render(request,'detail.html',context)