from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve
from django.views.decorators.cache import cache_page

# Configurar Django Admin para usar /login/
admin.site.login_url = 'login'

# Cache por 1 hora (3600 segundos) para tornar o carregamento mais liso nas próximas visitas
cache_time = 60 * 60

urlpatterns = [
    path('admin/login/', RedirectView.as_view(url='/login/?next=/admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Landing canônica em '/'. Aliases antigos redirecionam (mesmo HTML).
    path('', cache_page(cache_time)(TemplateView.as_view(template_name='index.html')), name='pagina_vendas_principal'),
    path('vendas/', RedirectView.as_view(url='/', permanent=True), name='pagina_vendas'),
    path('pagina-vendas/', RedirectView.as_view(url='/', permanent=True), name='pagina_vendas_alt'),
    
    # Sistema movido para /sistema/
    path('sistema/', include('estoque.urls')),
    
    path('api/loja/', include('loja.urls_api', namespace='loja_api')),
    path('loja/', include('loja.urls')),
]

# Servir arquivos da página de vendas (imgs e videos com cache)
urlpatterns += [
    path('videos/<path:path>', cache_page(cache_time)(serve), {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'videos'}),
    path('vendas/videos/<path:path>', cache_page(cache_time)(serve), {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'videos'}),
    path('imgs/<path:path>', cache_page(cache_time)(serve), {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'imgs'}),
    path('vendas/imgs/<path:path>', cache_page(cache_time)(serve), {'document_root': settings.BASE_DIR / 'pagina-vendas' / 'imgs'}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
