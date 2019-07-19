from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.core.paginator import Paginator
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

# list/种类id/页码?sort=排序方式
class ListView(View):
    '''列表页'''
    def get(self,request,type_id,page):
        '''显示列表页'''
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取排序方式 获取分类商品的信息
        # sort=default 按照默认进行排序
        # sort=price 按照价格进行排序
        # sort=hot 按照销量进行排序
        sort = request.GET.get('sort')

        if sort=='price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort=='hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort='default'
            skus = GoodsSKU.objects.filter(type=type).order_by('id')
        # 对数据进行分页
        paginator = Paginator(skus,1)
        try:
            page=int(page)
        except Exception as e:
            page = 1
        if page>paginator.num_pages:
            page=paginator.num_pages
        # 获取第page页的内容
        skus_page= paginator.page(page)
        # 进行页码控制，页面上最多显示5个页码
        # 1.总数小于5页，显示所有页
        # 2.当前是后三页时，显示后5页
        # 3.当前为前三页时，显示1-5页
        # 4. 其他情况时，显示当前页的前两页和后两页
        page_num = paginator.num_pages
        if page_num<=5:
            pages = range(1,page_num+1)
        elif page<=3:
            pages = range(1,6)
        elif page_num-page<=2:
            pages = range(page_num-4,page_num+1)
        else:
            pages = range(range-2,range+3)
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]
        # 获取购物车商品数目
        cart_count = 0
        user = request.user
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
        # 组织模板上下文
        context={
            'type':type,
            'types':types,
            'skus_page':skus_page,
            'new_skus':new_skus,
            'cart_count':cart_count,
            'sort':sort,
            'pages':pages
        }

        return render(request,'list.html',context)