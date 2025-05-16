from account.models import ROLE_OWNER


def permission_callback_for_admin(request):
    if request.user.is_superuser:
        return True
    if request.user.is_anonymous:
        return False
    if request.user.role == ROLE_OWNER:
        return True
    return False