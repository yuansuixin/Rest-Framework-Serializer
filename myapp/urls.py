
from django.conf.urls import url

from myapp import views

urlpatterns = [
 # url(r'^users/',views.UsersView.as_view()),
 url(r'^(?P<version>[v1|v2]+)/users/$',views.UsersView.as_view(),name='uuu'),
 url(r'^(?P<version>[v1|v2]+)/django/$',views.DjangoView.as_view(),name='django'),
 url(r'^(?P<version>[v1|v2]+)/parser/$',views.ParserView.as_view(),name='parser'),
 url(r'^(?P<version>[v1|v2]+)/roles/$',views.RolesView.as_view(),name='roles'),
 url(r'^(?P<version>[v1|v2]+)/userinfo/$',views.UserinfoView.as_view(),name='userinfo'),
 url(r'^(?P<version>[v1|v2]+)/group/(?P<pk>\d+)$',views.GroupView.as_view(),name='gp'),
 url(r'^(?P<version>[v1|v2]+)/usergroup/$',views.UserGroupView.as_view(),name='usergroup'),

]
