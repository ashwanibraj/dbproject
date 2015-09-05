from django.conf.urls import patterns, url
from finapp import views


urlpatterns= patterns('',
        url(r'^$', views.signin, name = 'signin'), 
        url(r'^signup/$', views.signup, name = 'signup'), 
        url(r'^home/$', views.home, name = 'home'), 
        url(r'^logout/$', views.logout, name = 'logout'), 
        url(r'^company/$', views.company, name = 'company'), 
        url(r'^sector/$', views.sector, name = 'sector'), 
        url(r'^accounts/$', views.accounts, name = 'accounts'), 
        url(r'^shares/$', views.shares, name = 'shares'), 
        url(r'^reports/$', views.reports, name = 'reports'), 
        url(r'^adminrep/$', views.adminrep, name = 'adminrep'), 
        url(r'^brokerageupd/$', views.brokerageupd, name = 'brokerageupd'), 
	#url(r'^signup/$', views.user_main, name = 'signup_pg'),
	#url(r'^success/', views.createpg, name = 'createpg'),
	#url(r'^failure/', views.failure, name = 'failure'),
	#url(r'^home/(?P<username>\w+)/$', views.bloghome, name = 'bloghome'),	
)

