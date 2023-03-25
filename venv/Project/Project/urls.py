
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404 

# handler404 = 'homepage.views.error_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('projects/', include('campaignapp.urls')),
    path('', include('homepage.urls')),
    path('user/', include('user.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


