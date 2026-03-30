from mongoengine import *
import datetime

class User(Document):
    username = StringField(required = True, unique = True)
    password = StringField(required = True)
    name = StringField()
    email = EmailField(unique = True)
    phone = StringField(required = True)
    role = StringField(choices = ["Doctor", "Patient", "Admin"], default="Patient")
    is_active = BooleanField(default = True)
    created_at = DateTimeField(default = datetime.datetime.utcnow)
