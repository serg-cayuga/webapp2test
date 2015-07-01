import datetime
import json
import jinja2
import os
import webapp2

from google.appengine.ext import ndb
from handlers import Response
from webapp2_extras import routes


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class IndexHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


config = {
    'webapp2_extras.auth': {
        'user_model': 'models.UserModel',
        'user_attributes': ['full_name'],
    },
    'webapp2_extras.sessions': {
        'secret_key': '1m3v2_73df1-s3g@xr8oj8ii91jn1nl@m$ese!j*6q_th1rw0r'
    }
}


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ndb.Model):
            serialized_fields = getattr(o, 'serialized_fields', ['key'])
            obj = {}
            for key in serialized_fields:
                value = getattr(o, key)
                if isinstance(value, ndb.Key) and key != 'key':
                    obj[key] = value.get()
                else:
                    obj[key] = value
            return obj
        elif isinstance(o, ndb.Key):
            return o.id()
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, datetime.date):
            return o.isoformat()


class JSONResponse(webapp2.Response):
    def __init__(self, *args, **kwargs):
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(*args, **kwargs)


class JSONWSGIApplication(webapp2.WSGIApplication):
    response_class = JSONResponse

    def __init__(self, *args, **kwargs):
        super(JSONWSGIApplication, self).__init__(*args, **kwargs)
        self.router.set_dispatcher(self.__class__.custom_dispatcher)

    @staticmethod
    def custom_dispatcher(router, request, response):
        resp = router.default_dispatcher(request, response)
        if isinstance(resp, Response):
            if resp.status is not None:
                response.status = resp.status
            else:
                response.status = 200
            if resp.data is not None:
                response.write(JSONEncoder(ensure_ascii=False).encode(resp.data))
            return response
        # return resp
        raise ValueError('Response must be an instance of base `Response`.')


app = webapp2.WSGIApplication([
    ('/', IndexHandler),
], debug=True, config=config)


app_api = JSONWSGIApplication([
    routes.PathPrefixRoute('/api', [
        webapp2.Route('/login', 'handlers.LoginHandler'),
        webapp2.Route('/signup', 'handlers.SignupHandler'),
        webapp2.Route('/logout', 'handlers.LogoutHandler'),
        webapp2.Route('/get-auth-user', 'handlers.GetAuthUserHandler'),
        webapp2.Route('/users', 'handlers.UsersHandler'),
        webapp2.Route('/users/<user_id:\d+>/messages', 'handlers.MessagesHandler'),
    ])
], debug=True, config=config)
