from mongoengine import *
import datetime

class Sensor(Document):
    user = ReferenceField("User", required = True)
    data = DictField()
    timestamp = DateTimeField(default = datetime.datetime.utcnow)
