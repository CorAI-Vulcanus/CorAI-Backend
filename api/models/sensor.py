from mongoengine import *
import datetime

class SensorECG(EmbeddedDocument):
    v_mV = IntField(required = True)
    t_us = IntField(required = True)
    timestamp = DateTimeField(default = datetime.datetime.utcnow)

class AnalysisResult(EmbeddedDocument):
    label = StringField()          # AFIB | AFL | J | N
    confidence = FloatField()
    probabilities = DictField()    # {AFIB: 0.95, N: 0.04, ...}
    analyzed_at = DateTimeField(default = datetime.datetime.utcnow)

class Sensor(Document):
    user = ReferenceField("User", required=True)

    fs = IntField(required = True)
    n_samples = IntField(required = True)
    unit = StringField(required = True)
    freq_signal_Hz = IntField()
    ecg = EmbeddedDocumentListField(SensorECG)
    analysis = EmbeddedDocumentField(AnalysisResult)
    created_at = DateTimeField(default = datetime.datetime.utcnow)
