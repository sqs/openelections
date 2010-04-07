from django.http import HttpResponseRedirect
from django.contrib.auth import logout

def do_logout(request):
    del request.session['webauth_sunetid']
    request.session.save()

def logout(request):
    do_logout(request)
    return HttpResponseRedirect('/')