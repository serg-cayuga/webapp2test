from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import User


class UserModel(User):
    """https://webapp-improved.appspot.com/tutorials/auth.html"""

    full_name = ndb.StringProperty()
    email = ndb.StringProperty()

    serialized_fields = ['key', 'full_name', 'email', 'created']

    @classmethod
    def queryset(cls):
        return cls.query().order(cls.full_name)


class MessageModel(ndb.Model):
    """Models a messages' system."""

    sender = ndb.KeyProperty(kind=UserModel)
    receiver = ndb.KeyProperty(kind=UserModel)
    text = ndb.StringProperty()  # (indexed=False)
    datetime = ndb.DateTimeProperty(auto_now_add=True)

    serialized_fields = ['key', 'sender', 'receiver', 'text', 'datetime']
