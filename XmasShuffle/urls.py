from django.conf.urls import include, url, patterns
from django.contrib import admin

from registration import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'XmasShuffle.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^members/(?P<org_link>[a-fA-F0-9]{32})$', views.members, name='members'),
    url(r'^wish/(?P<member_link>[a-fA-F0-9]{32})', views.wish, name='wish'),
    url(r'^members/(?P<org_link>[a-fA-F0-9]{32})/shuffle', views.shuffle, name='shuffle'),
    url(r'^admin/', include(admin.site.urls)),
]

# Django-RQ url
urlpatterns += patterns('',
    url(r'^django-rq/', include('django_rq.urls')),
)
