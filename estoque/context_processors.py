from .mixins import is_admin_master, get_user_lojas

def loja_context(request):
    if not request.user.is_authenticated:
        return {'is_admin_master': False, 'user_lojas': []}

    return {
        'is_admin_master': is_admin_master(request.user),
        'user_lojas': get_user_lojas(request.user),
    }
