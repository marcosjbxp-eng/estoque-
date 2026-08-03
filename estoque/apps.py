from django.apps import AppConfig

class EstoqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estoque'
    verbose_name = 'Controle de Estoque Multi-Loja'

    def ready(self):
        import estoque.signals  # noqa
