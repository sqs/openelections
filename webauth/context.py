
def webauth_context(request):
    return {'sunetid': request.session.get('webauth_sunetid', None)}