"""ABtroubleshooting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import url,include
from ABapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$',views.Homepage.as_view(),name='home'),
    url(r'^register/$',views.Registration,name='Register'),
    url(r'^base/$',views.index,name='index'),
    url(r'^ABapp/',include('ABapp.urls')),
    url(r'^loadexcel/',views.simple_upload,name='upload'),
    url(r'^sitestatus/$',views.kragha,name='Sitestatus'),
    url(r'^sitemessage/$',views.kragha1,name='Sitestatus1'),
    url(r'^run/$', views.Runpage.as_view(),name='run'),
    url(r'^setpassword/$',views.change_password,name='change_password'),
    url(r'^csv/$', views.export, name='export'),
    url(r'^all/$', views.exportall, name='exportall'),
    url(r'^sitedump/', views.exportsite, name='Sitedump'),
    url(r'^template/$', views.template, name='template'),
    url(r'^buyable/', views.Buyablestatus.as_view(), name='Buyable'),
    url(r'^buyableall/', views.Buyablestatusall.as_view(), name='Buyableall'),
    url(r'^error/$', views.Error.as_view(), name='Error'),
    url(r'^sitedata/', views.Sitestatusall.as_view(), name='Siteresult'),
    # url(r'^input/$', views.input, name='input'),
    # url(r'^HCsavings/$', views.HCdata, name='HCdata'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
