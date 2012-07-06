# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cgi
import time, datetime

from django import http
from django.template import Context, loader
from django.shortcuts import get_object_or_404

import settings

from models import Paste

import unicodedata
import datetime

titl = getattr(settings, 'SIMPYL_PASTEBIN_TITLE', 'Simpyl Pastebin')

def set_cookie(response, key, value, days_expire = 7):
    if not hasattr(settings, 'SESSION_COOKIE_DOMAIN') or not hasattr(settings, 'SESSION_COOKIE_SECURE'):
        return None
    
    if days_expire is None:
        max_age = 365*24*3600
    else:
        max_age = days_expire*24*3600
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
    return response

def sanitize_nasty(txt) :
    if not isinstance(txt, str) :
        txt = unicodedata.normalize('NFKD', txt).encode('ascii','ignore')
    return (''.join([c for c in txt if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_- .,^']))

def to_ascii_lazy(txt) :
    if not isinstance(txt, str) :
      return unicodedata.normalize('NFKD', txt).encode('ascii','ignore')
    else :
      return txt

def sanitize_username(user_name) :
    return sanitize_nasty(user_name)[:64]

def main(request):
    previous = request.POST.get('paste', '')

    user_name = ''

    user_name_post = request.POST.get('user_name', '')

    if 'user_name' in request.COOKIES :
        user_name = sanitize_username(request.COOKIES['user_name'])
    
    if user_name_post :
        user_name = sanitize_username(user_name_post)

    ucookie = False

    if previous:
        if not user_name :
            try :
                user_name = sanitize_username(request.META['HTTP_X_REAL_IP'])
            except :
                user_name = request.META['REMOTE_ADDR']
        else :
            ucookie = user_name

        title = to_ascii_lazy(request.POST.get('title', 'untitled'))
        tsms = long(time.time() * 1000)

        hash_inputs = [previous.encode("utf-8"), user_name + '-' + str(tsms)]
        try:
            import hashlib
            hasher = lambda hash_input: hashlib.md5(hash_input).hexdigest()
        except:
            import md5
            hasher = lambda hash_input: md5.new(hash_input).hexdigest()

        hash = ''.join([hasher(hash_input) for hash_input in hash_inputs])

        id = None

        for idsize in range(1, len(hash) + 1) :
            useid = 'p' + hash[0:idsize]

            try :
                Paste.objects.get(url=useid)
            except :
                id = useid
                break

        if id :
            p = Paste(content=previous, url=id, user_name=user_name, title=title, tsms=tsms)
            p.save()
        
            host = sanitize_nasty(request.get_host())
            if hasattr(settings, 'SIMPYL_SEARCH_PATH_OK') :
                if host.endswith('.' + settings.SIMPYL_SEARCH_PATH_OK) :
                    host = host[0:-len(settings.SIMPYL_SEARCH_PATH_OK)-1]
        
            previous = 'http://%s/%s' % (host, id)

            if hasattr(settings, 'SIMPYL_PASTEBIN_ZMQ_URL') :
                import zmq
                ztx = zmq.Context()
                pub = ztx.socket(zmq.PUB)
                pub.connect(settings.SIMPYL_PASTEBIN_ZMQ_URL)

                zm_action = "action::paste '%s' by %s: %s" % (title, user_name, previous)
                pub.send(zm_action)
            
    t = loader.get_template('index.html')

    cdict = {
        'title': titl,
        'title_low': titl.lower(),
        'previous': previous,
        'user_name': user_name
    }

    if hasattr(settings, 'SIMPYL_PASTEBIN_NOTELINE') :
        cdict['noteline'] = settings.SIMPYL_PASTEBIN_NOTELINE

    if hasattr(settings, 'GA_ID') :
        cdict['GA_ID'] = settings.GA_ID

    c = Context(cdict)
    
    resp = http.HttpResponse(t.render(c))
    if ucookie :
        set_cookie(resp, 'user_name', ucookie, days_expire=365)
    return resp

def fetch_paste(request):
    url = request.META.get('PATH_INFO', '')[1:]
    content = ""
    
    try:
        p = Paste.objects.get(url=url)
    except:
        t = loader.get_template('index.html')
        c = Context({
        'title': titl + ' 404',
        'title_low': titl.lower() + ' 404',
            'error': "Paste requested does not exist, or internal error."
        })
        return http.HttpResponse(t.render(c))
   
    repl = [
        ("\t", "  "),
        (" ", "&nbsp;"),
        ("\n","<br />")
    ]

    esc_text = cgi.escape(p.content)
    for a,b in repl :
        esc_text = esc_text.replace(a,b)

    if hasattr(settings, 'SIMPYL_PASTEBIN_NOTELINE') :
        noteline = cgi.escape(settings.SIMPYL_PASTEBIN_NOTELINE)
    else :
        noteline = ''

    when = 'unknown time'
    if p.tsms :
      when = datetime.datetime.fromtimestamp(int(p.tsms)/1000)


    title = 'paste: %s by \"%s\" at %s.' % (cgi.escape(p.title), cgi.escape(p.user_name), when)
    return http.HttpResponse("<html><head><title>%s</title></head><body><h1>%s</h1><br /><a href=\"/\">make another</a><br />%s<br /><br /><tt>%s</tt></body></html>" % (title, title, noteline, esc_text))
