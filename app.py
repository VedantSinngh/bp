from flask import Flask, render_template, jsonify
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import os

import time

app = Flask(__name__)

class PPGBasedBPEstimator:
    def __init__(self):
        self.frame_rate = 30
        self.buffer_size = 300  # 10 seconds of data
        
    def bandpass_filter(self, data, lowcut=0.5, highcut=5.0, order=5):

        if len(data) <= 33:
            return data
        if len(data) <= 33:  # Ensure the signal is longer than the filter's padding length
            return data  # Return the original signal if it's too short
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
        
        systolic = 120 + np.sum(features * systolic_coef)
        diastolic = 80 + np.sum(features * diastolic_coef)
        
        return systolic, diastolic
    
    def generate_sample_ppg(self):
        # Generate synthetic PPG data for demonstration
        t = np.linspace(0, 10, self.buffer_size)
        signal = 5 * np.sin(2 * np.pi * 1.2 * t) + 0.5 * np.sin(2 * np.pi * 5 * t)
        signal += np.random.normal(0, 0.3, len(t))
        return signal
    
    def run(self):
        try:

            # Simulate processing delay
            time.sleep(5)
            
            ppg_signal = self.generate_sample_ppg()

            while len(self.ppg_buffer) < self.buffer_size:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                ppg_value = self.process_frame(frame)
                self.ppg_buffer.append(ppg_value)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            cap.release()
            cv2.destroyAllWindows()

            ppg_signal = np.array(self.ppg_buffer)
            print(f"Length of PPG signal: {len(ppg_signal)}")  # Debugging
            
            if len(ppg_signal) <= 33:
                return {"error": "Insufficient data for filtering"}
  
            filtered_signal = self.bandpass_filter(ppg_signal)
            features = self.extract_features(filtered_signal)
            
            if features is not None:
                systolic, diastolic = self.estimate_bp(features[0])
                result = {
                    'systolic': round(np.clip(systolic, 90, 180), 1),
                    'diastolic': round(np.clip(diastolic, 60, 120), 1),
                    'heart_rate': round(np.clip(features[0][5], 50, 120), 1)
                }
                return result
            return {"error": "Unable to extract features"}
            
        except Exception as e:
            return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/estimate', methods=['POST'])
def estimate():
    estimator = PPGBasedBPEstimator()
    result = estimator.run()
    return jsonify(result)

if __name__ == '__main__':
  ]
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    port = int(os.getenv('PORT', 10000))  # Use PORT environment variable or default to 10000
    app.run(host='0.0.0.0', port=port)

