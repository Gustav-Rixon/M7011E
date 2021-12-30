from flask.wrappers import Request
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.serving import run_simple
from werkzeug.wrappers import Response

import os
import redis
from werkzeug.urls import url_parse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.wsgi import responder


url_map = Map([
    Rule('/index', endpoint='index'),
    Rule('/test', endpoint='index'),
])


def on_index(request):
    return Response('Hello from the index')


def on_test(request):
    print(1+1)
    return Response('Hello from the index')


views = {'index': on_index,
         'test': on_test}


@responder
def application(environ, start_response):
    request = Request(environ)
    urls = url_map.bind_to_environ(environ)
    return urls.dispatch(lambda e, v: views[e](request, **v),
                         catch_http_exceptions=True)


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    #app = create_app()
    run_simple('127.0.0.1', 5000, application,
               use_debugger=True, use_reloader=True)
