
def permission_callback(request):
    if request.user.is_superuser:
        return True
    return False
