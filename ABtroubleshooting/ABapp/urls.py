from django.conf.urls import url
from ABapp import views

app_name = 'ABapp'

urlpatterns = [
    url(r'^log_user/$',views.log_user,name='log_user'),
    url(r'^logout$',views.logguserout, name='log_out'),
]
