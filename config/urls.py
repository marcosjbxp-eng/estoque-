from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('vendas/', TemplateView.as_view(template_name='index.html'), name='pagina_vendas'),
    path('pagina-vendas/', TemplateView.as_view(template_name='index.html'), name='pagina_vendas_alt'),
    path('videos/<path:path>', serve, {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'videos'}),
    path('vendas/videos/<path:path>', serve, {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'videos'}),
    path('imgs/<path:path>', serve, {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'imgs'}),
    path('vendas/imgs/<path:path>', serve, {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'imgs'}),
    path('', include('estoque.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
