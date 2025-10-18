from django.contrib import admin
from django.urls import path, include
from eventos import views as eventos_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('eventos.urls', namespace='eventos')),
    path('accounts/', include('django.contrib.auth.urls')),    # login/logout/password...
    path('accounts/signup/', eventos_views.signup, name='signup'),
]
