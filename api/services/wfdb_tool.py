import numpy as np 
import wfdb

ecg_signal = [
    0.10, 0.12, 0.15, 0.14, 0.13,
    0.11, 0.09, 0.08, 0.07, 0.06,
    0.05, 0.05, 0.06, 0.08, 0.10,
    0.13, 0.16, 0.20, 0.18, 0.15,
]

fs = 250.0
record_name = "ecg_demo"

def main():
    p_signal = np.array(ecg_signal, dtype=float).reshape(-1, 1)
    wfdb.wrsamp(
        record_name = record_name,
        fs = fs,
        units = ['mV'],
        sig_name = ['ECG'],
        p_signal = p_signal,
        fmt = ['16'],
    )
    print(f"Archivos creados: {record_name}.hea y {record_name}.dat")

if __name__ == "__main__":
    main()
