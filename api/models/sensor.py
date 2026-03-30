from mongoengine import *
import datetime

class SensorECG(EmbeddedDocument):
    v_mV = IntField(required = True)
    t_us = IntField(required = True)
    timestamp = DateTimeField(default = datetime.datetime.utcnow)

class Sensor(Document):
    user = ReferenceField("User", required=True)

    fs = IntField(required = True)
    n_samples = IntField(required = True)
    unit = StringField(required = True)
    freq_signal_Hz = IntField()
    ecg = EmbeddedDocumentListField(SensorECG)
    created_at = DateTimeField(default = datetime.datetime.utcnow)
