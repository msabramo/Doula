def groupfinder(user_id, request):
    user = request.user
    if user is not None:
        auth_user = user.auth_user
        return [group.name for group in auth_user.auth_groups]
    return None
