from django.contrib import admin
from goods.models import GoodsType,GoodsSKU,Goods,GoodsImage,IndexGoodsBanner,IndexTypeGoodsBanner,IndexPromotionBanner
# Register your models here.
admin.site.register(GoodsType)
admin.site.register(GoodsSKU)
admin.site.register(Goods)
admin.site.register(GoodsImage)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexPromotionBanner)