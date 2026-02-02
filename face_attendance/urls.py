from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings 

urlpatterns = [
    # path('', lambda request: redirect('login_view')), 
        path('', lambda request: redirect('login_view')), 
    path('admin/', admin.site.urls),
    path('', include('face_app.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)