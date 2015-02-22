from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns=[]
if settings.DEBUG:
    #add url patterns for MEDIA files(user upload)
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    #add url patterns for STATIC files(eg. images, js, css files)
    urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
    url(r'^core/', include('core.urls')),
    url(r'^core2/', include('core2.urls')),
    url(r'^admin/', include(admin.site.urls)),
)