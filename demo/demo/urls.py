from django.contrib import admin
admin.autodiscover()

from django.conf.urls import patterns,url,include

urlpatterns = patterns('demo.views',    
    (r'^$','efforia_main'),
    (r'^admin/',include(admin.site.urls)),
    (r'^socialize/',include('socialize.urls')),
    (r'^spreadapp','init_spread'),
    (r'^products','store_main'),
    (r'^cancel','cancel'),
    (r'^delivery','delivery'),
    (r'^correios','mail'),
    (r'^spreadable','spreadable'),
    (r'^spreaded','spreaded'),
    (r'^spreadspread','spreadspread'),
    (r'^spread','main'),
    (r'^playable','playable'),
    (r'^images','image'),
    (r'^image','imageview'),
    (r'^contents','content'),
    (r'^expose','upload'),
    (r'^media','media'),
    (r'^productimage','product_image'),
) 
