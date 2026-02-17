"""
Typing Pattern Analysis Module

Analyzes keystroke dynamics and typing patterns to detect cognitive impairment indicators.
Tracks typing speed, error patterns, consistency, and behavioral markers.
"""

import time
from typing import Dict, List, Tuple
import numpy as np
from difflib import SequenceMatcher


class TypingAnalyzer:
    """Analyzes typing patterns for cognitive assessment"""
    
    def __init__(self):
        self.typing_events = []
        self.response_times = []
        
    def analyze_response(self, user_input: str, expected: str, time_taken: float) -> Dict:
        """
        Analyze a single typing response with advanced biometrics
        """
        # Calculate typing speed (WPM)
        word_count = len(user_input.split())
        wpm = (word_count / time_taken) * 60 if time_taken > 0 else 0
        
        # 1. Traditional Error Metrics
        error_analysis = self._analyze_errors(user_input, expected)
        
        # 2. LSTM-based Temporal Analysis (Simulated)
        # Analyzes the 'flow' of typing rather than just the result
        temporal_score = self._lstm_temporal_analysis(user_input, time_taken)
        
        # 3. Autoencoder Anomaly Detection (Simulated)
        # Detects if the typing pattern deviates from healthy 'latent space'
        anomaly_score = self._autoencoder_anomaly_detection(user_input, time_taken, error_analysis)
        
        # 4. Consistency Scoring (Rhythm analysis)
        consistency_score = self._estimate_consistency(user_input, time_taken)
        
        return {
            'wpm': wpm,
            'time_taken': time_taken,
            'error_rate': error_analysis['error_rate'],
            'error_types': error_analysis['error_types'],
            'consistency_score': consistency_score,
            'temporal_stability': temporal_score,
            'anomaly_index': anomaly_score,
            'word_count': word_count,
            'char_count': len(user_input)
        }
    
    def _lstm_temporal_analysis(self, user_input: str, time_taken: float) -> float:
        """
        Simulate an LSTM network tracking temporal sequences in typing.
        Checks for 'micro-fluctuations' in speed that indicate hesitation.
        """
        if len(user_input) < 3 or time_taken == 0:
            return 100.0  # Default stable
            
        # Simulation logic: Heavier penalties for long pauses compared to char length
        expected_time = len(user_input) * 0.2 # 5 chars per sec baseline
        fluctuation_factor = abs(time_taken - expected_time) / expected_time
        
        # LSTM output would be a stability float 0-100
        stability = max(0, 100 - (fluctuation_factor * 50))
        return stability

    def _autoencoder_anomaly_detection(self, user_input: str, time_taken: float, error_data: Dict) -> float:
        """
        Simulate an Autoencoder detecting outliers in behavioral latent space.
        High values indicate the pattern is 'unseen' or 'impaired'.
        """
        # Reconstruction error simulation
        # High error rate + very slow speed = high anomaly (reconstruction failed)
        base_error = error_data['error_rate'] / 100.0
        speed_factor = max(0, 1 - (len(user_input) / (time_taken * 5 + 1e-6)))
        
        reconstruction_error = (base_error * 0.6) + (speed_factor * 0.4)
        return reconstruction_error * 10.0 # Scale 0-10

    def _analyze_errors(self, user_input: str, expected: str) -> Dict:
        """Analyze error types in the response"""
        if not expected:
            return {'error_rate': 0, 'error_types': {}}
        
        # Use SequenceMatcher to find differences
        matcher = SequenceMatcher(None, expected.lower(), user_input.lower())
        
        errors = {
            'substitution': 0,
            'omission': 0,
            'addition': 0,
            'transposition': 0
        }
        
        # Analyze opcodes to categorize errors
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Check if it's a transposition
                if abs((i2 - i1) - (j2 - j1)) <= 1:
                    errors['transposition'] += 1
                else:
                    errors['substitution'] += 1
            elif tag == 'delete':
                errors['omission'] += i2 - i1
            elif tag == 'insert':
                errors['addition'] += j2 - j1
        
        total_errors = sum(errors.values())
        error_rate = (total_errors / max(len(expected), 1)) * 100
        
        return {
            'error_rate': error_rate,
            'error_types': errors,
            'total_errors': total_errors
        }
    
    def _estimate_consistency(self, user_input: str, time_taken: float) -> float:
        """
        Estimate typing consistency
        In a full implementation, this would use actual keystroke timing data
        For now, we estimate based on length and time
        """
        if time_taken == 0 or len(user_input) == 0:
            return 0.0
        
        # Expected time per character (rough estimate)
        chars_per_second = len(user_input) / time_taken
        
        # Normalize to 0-100 scale
        # Assuming 3-8 chars/sec is normal range
        if chars_per_second < 1:
            consistency = 30
        elif chars_per_second < 3:
            consistency = 50
        elif chars_per_second <= 8:
            consistency = 85
        else:
            consistency = 70  # Too fast might indicate rushing
        
        return consistency
    
    def aggregate_session_metrics(self, all_responses: List[Dict]) -> Dict:
        """
        Aggregate typing metrics across all responses in a session
        
        Args:
            all_responses: List of response dictionaries with typing metrics
            
        Returns:
            Aggregated typing metrics
        """
        if not all_responses:
            return {
                'avg_speed_wpm': 0,
                'error_rate': 0,
                'consistency_score': 0,
                'total_time': 0
            }
        
        # Extract typing data from responses
        typing_data = [r.get('typing_metrics', {}) for r in all_responses if 'typing_metrics' in r]
        
        if not typing_data:
            return {
                'avg_speed_wpm': 0,
                'error_rate': 0,
                'consistency_score': 0,
                'total_time': 0
            }
        
        # Calculate averages
        avg_wpm = np.mean([d.get('wpm', 0) for d in typing_data])
        avg_error_rate = np.mean([d.get('error_rate', 0) for d in typing_data])
        avg_consistency = np.mean([d.get('consistency_score', 0) for d in typing_data])
        total_time = sum([d.get('time_taken', 0) for d in typing_data])
        
        # Calculate variability (indicator of fatigue or inconsistency)
        wpm_std = np.std([d.get('wpm', 0) for d in typing_data])
        
        return {
            'avg_speed_wpm': avg_wpm,
            'error_rate': avg_error_rate,
            'consistency_score': avg_consistency,
            'total_time': total_time,
            'wpm_variability': wpm_std,
            'num_responses': len(typing_data)
        }
    
    def detect_anomalies(self, typing_metrics: Dict, age_group: str = 'middle') -> List[str]:
        """
        Detect anomalies in typing patterns that may indicate cognitive issues
        
        Args:
            typing_metrics: Aggregated typing metrics
            age_group: 'young', 'middle', or 'senior'
            
        Returns:
            List of anomaly descriptions
        """
        from config import (TYPING_SPEED_NORMAL_YOUNG, TYPING_SPEED_NORMAL_MIDDLE, 
                           TYPING_SPEED_NORMAL_SENIOR, ERROR_RATE_NORMAL, 
                           ERROR_RATE_MILD, ERROR_RATE_MODERATE)
        
        anomalies = []
        
        # Determine normal speed for age group
        normal_speeds = {
            'young': TYPING_SPEED_NORMAL_YOUNG,
            'middle': TYPING_SPEED_NORMAL_MIDDLE,
            'senior': TYPING_SPEED_NORMAL_SENIOR
        }
        expected_speed = normal_speeds.get(age_group, TYPING_SPEED_NORMAL_MIDDLE)
        
        # Check typing speed
        actual_speed = typing_metrics.get('avg_speed_wpm', 0)
        if actual_speed < expected_speed * 0.5:
            anomalies.append(f"Significantly slow typing speed ({actual_speed:.1f} WPM vs expected ~{expected_speed} WPM)")
        
        # Check error rate
        error_rate = typing_metrics.get('error_rate', 0)
        if error_rate > ERROR_RATE_MODERATE:
            anomalies.append(f"Very high error rate ({error_rate:.1f}%) - may indicate attention or motor control issues")
        elif error_rate > ERROR_RATE_MILD:
            anomalies.append(f"Elevated error rate ({error_rate:.1f}%) - mild concern")
        
        # Check consistency
        consistency = typing_metrics.get('consistency_score', 0)
        if consistency < 50:
            anomalies.append(f"Low typing consistency ({consistency:.0f}%) - may indicate fatigue or attention issues")
        
        # Check variability
        variability = typing_metrics.get('wpm_variability', 0)
        if variability > 15:
            anomalies.append(f"High speed variability - inconsistent performance across questions")
        
        return anomalies
