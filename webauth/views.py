from django.http import HttpResponseRedirect
from django.contrib.auth import logout

def logout(request):
    del request.session['webauth_sunetid']
    request.session.save()
    return HttpResponseRedirect('/')