from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
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