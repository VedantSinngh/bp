# app.py
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt

app = Flask(__name__)

class PPGBasedBPEstimator:
    def __init__(self):
        self.frame_rate = 30
        self.roi_size = 100
        self.buffer_size = 300
        self.ppg_buffer = []
    
    def bandpass_filter(self, data, lowcut=0.5, highcut=5.0, order=5):
        nyquist = 0.5 * self.frame_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, data)
    
    def extract_features(self, signal):
        peaks, _ = find_peaks(signal, distance=10)
        valleys, _ = find_peaks(-signal, distance=10)
        
        if len(peaks) < 2 or len(valleys) < 2:
            return None
        
        peak_amplitudes = signal[peaks]
        valley_amplitudes = signal[valleys]
        
        features = {
            'mean_peak_amplitude': np.mean(peak_amplitudes),
            'std_peak_amplitude': np.std(peak_amplitudes),
            'mean_valley_amplitude': np.mean(valley_amplitudes),
            'pulse_width': np.mean(np.diff(peaks)),
            'peak_valley_ratio': np.mean(peak_amplitudes) / np.mean(valley_amplitudes),
            'heart_rate': len(peaks) * (60 / (len(signal) / self.frame_rate))
        }
        
        return np.array(list(features.values())).reshape(1, -1)
    
    def estimate_bp(self, features):
        systolic_coef = np.array([2.5, 0.8, -1.2, 1.5, 0.6, 0.3])
        diastolic_coef = np.array([1.8, 0.5, -0.8, 1.2, 0.4, 0.2])
        
        systolic_base = 120
        diastolic_base = 80
        
        systolic = systolic_base + np.sum(features * systolic_coef)
        diastolic = diastolic_base + np.sum(features * diastolic_coef)
        
        return systolic, diastolic
    
    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        roi = gray[h//2 - self.roi_size//2:h//2 + self.roi_size//2,
                   w//2 - self.roi_size//2:w//2 + self.roi_size//2]
        return np.mean(roi)
    
    def run(self):
        cap = cv2.VideoCapture(0)
        try:
            while len(self.ppg_buffer) < self.buffer_size:
                ret, frame = cap.read()
                if not ret:
                    break
                ppg_value = self.process_frame(frame)
                self.ppg_buffer.append(ppg_value)
            
            ppg_signal = np.array(self.ppg_buffer)
            filtered_signal = self.bandpass_filter(ppg_signal)
            features = self.extract_features(filtered_signal)
            
            if features is not None:
                systolic, diastolic = self.estimate_bp(features[0])
                result = {
                    'systolic': round(systolic, 1),
                    'diastolic': round(diastolic, 1),
                    'heart_rate': round(features[0][5], 1)
                }
                return result
            return {"error": "Unable to extract features"}
        
        finally:
            cap.release()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/measure', methods=['POST'])
def measure():
    try:
        estimator = PPGBasedBPEstimator()
        result = estimator.run()
        return jsonify(result)
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error in /measure: {str(e)}")
        # Return a JSON error response
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)