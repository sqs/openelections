from django.http import HttpResponseRedirect 
from django.http import HttpResponseServerError
from lxml import etree
import urllib2

AUTH_URL = "https://weblogin.stanford.edu" 
CAS_NS = {'cas': 'http://www.yale.edu/tp/cas'}

def webauth_required2(function):
  def _dec(view_func):
    def _view(request, *args, **kwargs):
      if request.session.get('webauth', False): 
        return view_func(request, *args, **kwargs)
      ticket = request.GET.get("ticket", False)
      if ticket:
        try:
          url = request.session.get('url', '')
          handle = urllib2.urlopen(AUTH_URL + "/serviceValidate?service=" + url + "&ticket=" + ticket)
        except IOError, e:
          return HttpResponseServerError()
	tree = etree.parse(handle)
	request.session['webauth'] = (len(tree.xpath('//cas:authenticationSuccess', namespaces=CAS_NS)) == 1)
	if request.session['webauth']:
	  request.session['netid'] = tree.xpath('//cas:user', namespaces=CAS_NS)[0].text
          return view_func(request, *args, **kwargs)
      else:
        request.session['url'] = urllib2.quote(request.build_absolute_uri())
        return HttpResponseRedirect(AUTH_URL + "/login?service=" + request.session['url'])
    _view.__name__ = view_func.__name__
    _view.__dict__ = view_func.__dict__
    _view.__doc__ = view_func.__doc__
    
    return _view
  return _dec(function)

WEBAUTH_URL = "http://stanford.edu/~sqs/cgi-bin/authenticate_elections2.php?from="

def webauth_required(function):
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if 'webauth_sunetid' in request.session:
                return view_func(request, *args, **kwargs)
            elif 'webauth_sunetid' in request.GET:
                request.session['webauth_sunetid'] = request.GET['webauth_sunetid']
                return view_func(request, *args, **kwargs)
            else:
                url = urllib2.quote(request.build_absolute_uri())
                return HttpResponseRedirect(WEBAUTH_URL + url)
        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__
        return _view
    return _dec(function)
