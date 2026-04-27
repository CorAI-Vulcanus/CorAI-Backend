import os
import logging
import numpy as np
import joblib
from math import gcd
from scipy.signal import butter, filtfilt, find_peaks, resample_poly
import pywt

logger = logging.getLogger(__name__)

_ARTIFACTS_DIR = os.getenv(
    "AI_ARTIFACTS_DIR",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "CorAI-AI", "results_retrained"),
)

_clf = None
_scaler = None
_label_encoder = None
_feature_columns = None
_col_medians = None

TARGET_FS = 250.0
WAVELET_NAME = "db4"
WAVELET_LEVELS = 4


def load_artifacts():
    global _clf, _scaler, _label_encoder, _feature_columns, _col_medians

    path = os.path.abspath(_ARTIFACTS_DIR)
    logger.info("Loading AI artifacts from: %s", path)

    _clf = joblib.load(os.path.join(path, "afdb_rhythm_classifier.joblib"))
    _scaler = joblib.load(os.path.join(path, "afdb_scaler.joblib"))
    _label_encoder = joblib.load(os.path.join(path, "afdb_label_encoder.joblib"))
    _feature_columns = joblib.load(os.path.join(path, "afdb_feature_columns.joblib"))
    _col_medians = joblib.load(os.path.join(path, "afdb_col_medians.joblib"))

    logger.info("AI artifacts loaded. Classes: %s", list(_label_encoder.classes_))


# ---------------------------------------------------------------------------
# Signal preprocessing
# ---------------------------------------------------------------------------

def _resample(signal: np.ndarray, src_fs: float, dst_fs: float) -> np.ndarray:
    if src_fs == dst_fs:
        return signal
    src_int, dst_int = int(round(src_fs)), int(round(dst_fs))
    common = gcd(dst_int, src_int)
    return resample_poly(signal, dst_int // common, src_int // common).astype(signal.dtype)


def _bandpass(signal: np.ndarray, fs: float, lowcut=0.5, highcut=40.0, order=4) -> np.ndarray:
    nyq = 0.5 * fs
    min_len = 3 * (order * 2 + 1) * 2
    if len(signal) < min_len:
        return signal
    try:
        b, a = butter(order, [lowcut / nyq, highcut / nyq], btype="band")
        return filtfilt(b, a, signal).astype(signal.dtype)
    except Exception:
        return signal


# ---------------------------------------------------------------------------
# Feature extraction (mirrors afdb_dataset_loader.py exactly)
# ---------------------------------------------------------------------------

def _temporal(signal: np.ndarray) -> dict:
    return {
        "mean": float(np.mean(signal)),
        "std": float(np.std(signal)),
        "median": float(np.median(signal)),
        "min": float(np.min(signal)),
        "max": float(np.max(signal)),
        "rms": float(np.sqrt(np.mean(signal ** 2))),
        "zcr": float(((signal[:-1] * signal[1:]) < 0).sum() / max(1, len(signal) - 1)),
    }


def _detect_rpeaks(signal: np.ndarray, fs: float) -> np.ndarray:
    nyq = 0.5 * fs
    if nyq <= 7.5:
        return np.array([], dtype=int)
    try:
        b, a = butter(3, [5.0 / nyq, min(15.0 / nyq, 0.99)], btype="band")
        sig_f = filtfilt(b, a, signal)
    except Exception:
        sig_f = signal

    diff_sig = np.ediff1d(sig_f, to_begin=0)
    integrated = np.convolve(diff_sig ** 2, np.ones(max(1, int(0.12 * fs))) / max(1, int(0.12 * fs)), mode="same")
    peaks, _ = find_peaks(integrated, distance=int(0.2 * fs), height=np.percentile(integrated, 75))

    rpeaks = []
    radius = int(0.03 * fs)
    for p in peaks:
        left, right = max(p - radius, 0), min(p + radius, len(sig_f) - 1)
        window = sig_f[left:right + 1]
        if window.size:
            rpeaks.append(int(left + np.argmax(np.abs(window))))
    return np.unique(rpeaks).astype(int)


def _rr_features(rpeaks: np.ndarray, fs: float) -> dict:
    if rpeaks is None or len(rpeaks) < 2:
        return {"rr_count": 0, "rr_mean": np.nan, "rr_std": np.nan, "rr_min": np.nan,
                "rr_max": np.nan, "rr_sdnn": np.nan, "rr_rmssd": np.nan, "rr_pnn50": np.nan}
    rr = np.diff(rpeaks) / float(fs)
    return {
        "rr_count": len(rr),
        "rr_mean": float(np.mean(rr)),
        "rr_std": float(np.std(rr)),
        "rr_min": float(np.min(rr)),
        "rr_max": float(np.max(rr)),
        "rr_sdnn": float(np.std(rr, ddof=1)) if rr.size > 1 else np.nan,
        "rr_rmssd": float(np.sqrt(np.mean(np.diff(rr) ** 2))) if rr.size > 1 else np.nan,
        "rr_pnn50": float(np.sum(np.abs(np.diff(rr)) > 0.05) / max(1, len(rr) - 1)),
    }


def _qrs_features(signal: np.ndarray, rpeaks: np.ndarray, fs: float) -> dict:
    empty = {"qrs_count": 0, "qrs_width_mean": np.nan, "qrs_width_std": np.nan,
             "qrs_amp_mean": np.nan, "qrs_amp_std": np.nan, "qrs_area_mean": np.nan}
    if rpeaks is None or len(rpeaks) == 0:
        return empty

    half = int(0.06 * fs)
    widths, amps, areas = [], [], []
    for r in rpeaks:
        left, right = max(r - half, 0), min(r + half, len(signal) - 1)
        seg = signal[left:right + 1]
        if seg.size == 0:
            continue
        amp = float(np.max(seg) - np.min(seg))
        amps.append(amp)
        areas.append(float(np.trapezoid(np.abs(seg))))
        trough = np.min(seg)
        half_amp = trough + 0.5 * amp
        l_idx, r_idx = r, r
        while l_idx > left and signal[l_idx] > half_amp:
            l_idx -= 1
        while r_idx < right and signal[r_idx] > half_amp:
            r_idx += 1
        widths.append(float((r_idx - l_idx) / fs))

    if not widths:
        return empty
    return {
        "qrs_count": len(widths),
        "qrs_width_mean": float(np.mean(widths)),
        "qrs_width_std": float(np.std(widths)),
        "qrs_amp_mean": float(np.mean(amps)),
        "qrs_amp_std": float(np.std(amps)),
        "qrs_area_mean": float(np.mean(areas)),
    }


def _wavelet_features(signal: np.ndarray) -> dict:
    if len(signal) < 8:
        return {}
    coeffs = pywt.wavedec(signal, WAVELET_NAME, level=WAVELET_LEVELS)
    feats = {}
    for i, c in enumerate(coeffs):
        arr = np.asarray(c, dtype=float)
        feats[f"wave_energy_L{i}"] = float(np.sum(arr ** 2))
        feats[f"wave_std_L{i}"] = float(np.std(arr))
        feats[f"wave_mean_L{i}"] = float(np.mean(arr))
    return feats


def _extract_features(signal: np.ndarray, fs: float) -> dict:
    signal = np.asarray(signal, dtype=float)
    feats = _temporal(signal)
    try:
        rpeaks = _detect_rpeaks(signal, fs)
    except Exception:
        rpeaks = np.array([], dtype=int)
    feats.update(_rr_features(rpeaks, fs))
    feats.update(_qrs_features(signal, rpeaks, fs))
    feats.update(_wavelet_features(signal))
    feats["n_rpeaks"] = int(len(rpeaks))
    feats["n_samples"] = int(len(signal))
    feats["fs"] = float(fs)
    return feats


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_ecg(v_mv_samples: list[int], fs: int) -> dict:
    """
    Run rhythm classification on a raw ECG signal.

    Parameters
    ----------
    v_mv_samples : list of int
        ECG voltage samples as stored in the backend (v_mV field).
    fs : int
        Sampling frequency of the input signal in Hz.

    Returns
    -------
    dict with keys:
        label        – predicted rhythm class (AFIB | AFL | J | N)
        confidence   – probability of the predicted class (0-1)
        probabilities – dict mapping each class to its probability
    """
    if _clf is None:
        raise RuntimeError("AI artifacts not loaded. Call load_artifacts() at startup.")

    signal = np.array(v_mv_samples, dtype=np.float32)
    signal = _resample(signal, float(fs), TARGET_FS)
    signal = _bandpass(signal, TARGET_FS)

    feats = _extract_features(signal, TARGET_FS)

    # Build feature vector in the exact column order the scaler expects
    row = np.array([feats.get(col, np.nan) for col in _feature_columns], dtype=np.float64)

    # Impute NaN with training-set medians
    nan_mask = np.isnan(row)
    row[nan_mask] = _col_medians[nan_mask]

    X = _scaler.transform(row.reshape(1, -1))
    pred_enc = _clf.predict(X)[0]
    label = _label_encoder.inverse_transform([pred_enc])[0]

    proba = _clf.predict_proba(X)[0]
    probabilities = {cls: round(float(p), 4) for cls, p in zip(_label_encoder.classes_, proba)}
    confidence = round(float(proba[pred_enc]), 4)

    return {"label": label, "confidence": confidence, "probabilities": probabilities}
