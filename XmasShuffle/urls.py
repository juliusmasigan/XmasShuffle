from django.conf.urls import include, url
from django.contrib import admin

from registration import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'XmasShuffle.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^(?P<org_link>[a-fA-F0-9]{32})/members/', views.members, name='members'),
    url(r'^admin/', include(admin.site.urls)),
]
