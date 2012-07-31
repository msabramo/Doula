def groupfinder(user_id, request):
    user = request.user
    if user is not None:
        return []
    return None
