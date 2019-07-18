
from django.conf.urls import url
from user.views import RigisterView,ActiveView,LoginView,LogoutView,UserInfoView,UserOrderView,AddressView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # url(r'^register$',views.register,name='register'),
    # url(r'^register_handle$',views.register_handle,name='register_handle'),
    url(r'^register$',RigisterView.as_view(),name='register'),
    url(r'^active/(.*)$',ActiveView.as_view(),name='acive'),
    url(r'^login$',LoginView.as_view(),name='login'),
    url(r'^logout$',LogoutView.as_view(),name = 'logout'),
    url(r'^$',UserInfoView.as_view(),name='user'),
    url(r'^order$',UserOrderView.as_view(),name='order'),
    url(r'^address$',AddressView.as_view(),name='address'),
]
