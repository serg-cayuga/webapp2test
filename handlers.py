import webapp2

from google.appengine.ext import ndb
from webapp2_extras import auth, json, sessions

from forms import SignUpForm, LoginForm, MessageForm
from models import UserModel, MessageModel


def login_required(handler_method):
    """A decorator gives access to a handler only for logged in user."""
    def check_login(self, *args, **kwargs):
        user = self.auth.get_user_by_session()
        if user is None:
            return Response(status=401)
        else:
            return handler_method(self, *args, **kwargs)

    return check_login


class Response(object):
    """
    Base response object.
    If status is not set - 200 on default.

    """
    def __init__(self, data=None, status=None):
        self.data = data
        self.status = status


class ResponseBadRequest(Response):
    def __init__(self, data=None):
        super(ResponseBadRequest, self).__init__(data, 400)


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            return webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def auth(self):
        """Shortcut to access the auth instance as a property."""
        return auth.get_auth()

    @webapp2.cached_property
    def user_model(self):
        """
        Returns the implementation of the user model.
        It is consistent with config['webapp2_extras.auth']['user_model'], if set.

        """
        return self.auth.store.user_model

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class SignupHandler(BaseHandler):

    def post(self):
        data = json.decode(self.request.body)
        form = SignUpForm(**data)
        if not form.validate():
            return ResponseBadRequest(form.errors)

        created, user = self.user_model.create_user(form.email.data, email=form.email.data,
                                                    password_raw=form.password.data, full_name=form.full_name.data)
        if not created:
            return ResponseBadRequest('Unable to create user. This email address is already exists')

        user_dict = self.auth.store.user_to_dict(user)
        self.auth.set_session(user_dict, remember=True)  # store user data in the session
        return Response(user_dict)


class LoginHandler(BaseHandler):

    def post(self):
        data = json.decode(self.request.body)
        form = LoginForm(**data)
        if not form.validate():
            return ResponseBadRequest(form.errors)
        try:
            user_dict = self.auth.get_user_by_password(form.email.data, form.password.data, remember=True)
        except auth.AuthError:
            return ResponseBadRequest('Invalid email or password')
        else:
            return Response(user_dict)


class LogoutHandler(BaseHandler):
    def get(self):
        self.auth.unset_session()
        return Response()


class GetAuthUserHandler(BaseHandler):
    def get(self):
        user = self.auth.get_user_by_session()
        if user is None:
            return Response(status=401)
        else:
            return Response(user)


class UsersHandler(BaseHandler):

    @login_required
    def get(self):
        auth_user = self.auth.get_user_by_session()
        users = UserModel.query(UserModel.key != ndb.Key('UserModel', auth_user['user_id'])).fetch()
        return Response(users)


class MessagesHandler(BaseHandler):

    @login_required
    def get(self, user_id):
        auth_user = self.auth.get_user_by_session()
        user_auth_key = ndb.Key('UserModel', auth_user['user_id'])
        user_key = ndb.Key('UserModel', int(user_id))

        query = ndb.OR(ndb.AND(MessageModel.sender == user_auth_key, MessageModel.receiver == user_key),
                       ndb.AND(MessageModel.sender == user_key, MessageModel.receiver == user_auth_key))
        messages = MessageModel.query(query).order(-MessageModel.datetime).fetch()
        return Response(messages)

    @login_required
    def post(self, user_id):
        auth_user = self.auth.get_user_by_session()
        user_auth_key = ndb.Key('UserModel', auth_user['user_id'])
        user_key = ndb.Key('UserModel', int(user_id))
        data = json.decode(self.request.body)
        form = MessageForm(**data)
        if not form.validate():
            return ResponseBadRequest(form.errors)

        message = MessageModel()
        message.sender = user_auth_key
        message.receiver = user_key
        message.text = form.text.data
        message.put()

        return Response(message)
