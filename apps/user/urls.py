
from django.conf.urls import url
from user.views import RigisterView

urlpatterns = [
    # url(r'^register$',views.register,name='register'),
    # url(r'^register_handle$',views.register_handle,name='register_handle'),
    url(r'^register$',RigisterView.as_view(),name='register'),
]
