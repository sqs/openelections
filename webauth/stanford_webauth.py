from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from lxml import etree
import urllib2
import hashlib
from django.conf import settings

AUTH_URL = "https://weblogin.stanford.edu" 
CAS_NS = {'cas': 'http://www.yale.edu/tp/cas'}

def make_secret_hash(sunetid):
    m = hashlib.md5()
    m.update(settings.WEBAUTH_SECRET + sunetid)
    return m.hexdigest()

def webauth_required(function):
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            # if 'webauth_sunetid' in request.session:
            #    del request.session['webauth_sunetid']
            #    del request.session['webauth_name']
            
            # debug sunetid login
            if settings.DEBUG and 'webauth_sunetid' in request.GET:
                request.session['webauth_sunetid'] = request.GET['webauth_sunetid']
                
            if 'webauth_sunetid' in request.session:
                return view_func(request, *args, **kwargs)
            elif 'webauth_sunetid' in request.GET:
                sunetid = request.GET['webauth_sunetid']
                actual_hash = request.GET['hash']
                #name = request.GET['name']
                
                expected_hash = make_secret_hash(sunetid)
                
                if expected_hash == actual_hash:
                    request.session['webauth_sunetid'] = sunetid
                    #request.session['webauth_name'] = name
                    
                    path_only = request.path
                    upto = request.path.find('?')
                    if upto != -1:
                        path_only = path_only[:upto]
                    return HttpResponseRedirect(path_only)
                else:
                    return HttpResponse("authentication error")
            else:
                url = urllib2.quote(request.build_absolute_uri())
                return HttpResponseRedirect(settings.WEBAUTH_URL + url)
        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__
        return _view
    return _dec(function)
