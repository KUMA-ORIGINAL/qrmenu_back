
def permission_callback(request):
    if request.user.is_superuser:
        return True
    return False

def permission_callback_for_admin(request):
    if request.user.is_superuser or request.user.role == 'owner':
        return True
    return False