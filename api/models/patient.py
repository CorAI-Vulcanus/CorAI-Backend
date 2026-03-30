from mongoengine import *
import datetime

class Patient(Document):
    user = ReferenceField("User", required=True)
    blood_type = StringField()
    sex = StringField(choices=["male","female","other"])
    weight = FloatField()
    height = FloatField()
