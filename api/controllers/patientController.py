import logging
from fastapi import HTTPException
from models.patient import Patient
from models.user import User
from models.sensor import Sensor, SensorECG, AnalysisResult
from schemas.patient import PatientUpdate
from schemas.sensor import SensorData
from bson import ObjectId
from bson.errors import InvalidId
from services.ai_inference import analyze_ecg

logger = logging.getLogger(__name__)


def _validate_id(user_id: str):
    try:
        ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


def get_patients(token: dict) -> list:
    if token.get("role") not in ("Doctor", "Admin"):
        raise HTTPException(status_code=403, detail="Forbidden action")

    patients = Patient.objects.all()
    result = []
    for p in patients:
        result.append({
            "id": str(p.id),
            "user_id": str(p.user.id),
            "blood_type": p.blood_type,
            "sex": p.sex,
            "weight": p.weight,
            "height": p.height,
        })
    return result


def get_patient(user_id: str, token: dict) -> dict:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    patient = Patient.objects(user=user).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "id": str(patient.id),
        "user_id": str(user.id),
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "blood_type": patient.blood_type,
        "sex": patient.sex,
        "weight": patient.weight,
        "height": patient.height,
    }


def update_patient(user_id: str, data: PatientUpdate, token: dict) -> dict:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    patient = Patient.objects(user=user).first()
    if not patient:
        patient = Patient(user=user)

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if updates:
        patient.update(**updates)
    else:
        patient.save()

    return {"message": "Patient data updated successfully"}


def ingest_data(user_id: str, data: SensorData, token: dict) -> dict:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ecg_entries = [
        SensorECG(v_mV=e.v_mV, t_us=e.t_us, timestamp=e.timestamp)
        for e in data.ecg
    ]

    sensor = Sensor(
        user=user,
        fs=data.fs,
        n_samples=data.n_samples,
        unit=data.unit,
        freq_signal_Hz=data.freq_signal_Hz,
        ecg=ecg_entries,
    )

    analysis_result = None
    try:
        samples = [e.v_mV for e in data.ecg]
        result = analyze_ecg(samples, data.fs)
        sensor.analysis = AnalysisResult(
            label=result["label"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
        )
        analysis_result = result
        logger.info("ECG analyzed: %s (confidence=%.2f)", result["label"], result["confidence"])
    except Exception as exc:
        logger.warning("AI inference failed, storing ECG without analysis: %s", exc)

    sensor.save()

    response = {"message": "ECG data received successfully"}
    if analysis_result:
        response["analysis"] = analysis_result
    return response


def get_sessions(user_id: str, token: dict) -> list:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return [
        {
            "id": str(s.id),
            "fs": s.fs,
            "n_samples": s.n_samples,
            "unit": s.unit,
            "freq_signal_Hz": s.freq_signal_Hz,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "ecg": [
                {"v_mV": e.v_mV, "t_us": e.t_us, "timestamp": e.timestamp.isoformat() if e.timestamp else None}
                for e in s.ecg
            ],
            "analysis": {
                "label": s.analysis.label,
                "confidence": s.analysis.confidence,
                "probabilities": s.analysis.probabilities,
                "analyzed_at": s.analysis.analyzed_at.isoformat() if s.analysis.analyzed_at else None,
            } if s.analysis else None,
        }
        for s in Sensor.objects(user=user).order_by("-created_at")
    ]
