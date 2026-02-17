"""
Feature Extraction Module for Cognitive Assessment

Extracts comprehensive features from assessment data for ML model input.
Features include cognitive scores, typing patterns, behavioral markers, and temporal patterns.
"""

import numpy as np
from typing import Dict, List


class FeatureExtractor:
    """Extract features from cognitive assessment data for ML models"""
    
    def __init__(self):
        self.feature_names = []
        
    def extract_features(self, responses: List[Dict], typing_metrics: Dict, 
                        session_metadata: Dict = None) -> Dict:
        """
        Extract all features from assessment data
        
        Args:
            responses: List of question responses with scores
            typing_metrics: Aggregated typing metrics
            session_metadata: Optional metadata (age, education, etc.)
            
        Returns:
            Dictionary of features for ML model
        """
        features = {}
        
        # Cognitive Features
        features.update(self._extract_cognitive_features(responses))
        
        # Typing Features
        features.update(self._extract_typing_features(typing_metrics))
        
        # Behavioral Features
        features.update(self._extract_behavioral_features(responses))
        
        # Domain-Specific Features
        features.update(self._extract_domain_features(responses))
        
        # Temporal Features
        features.update(self._extract_temporal_features(responses))
        
        # Metadata Features (if available)
        if session_metadata:
            features.update(self._extract_metadata_features(session_metadata))
        
        self.feature_names = list(features.keys())
        return features
    
    def _extract_cognitive_features(self, responses: List[Dict]) -> Dict:
        """Extract cognitive performance features"""
        if not responses:
            return {
                'total_score': 0,
                'max_possible_score': 0,
                'score_percentage': 0,
                'num_correct': 0,
                'num_partial': 0,
                'num_incorrect': 0
            }
        
        total_earned = sum(r.get('earned', 0) for r in responses)
        total_possible = sum(r.get('max_points', 0) for r in responses)
        
        # Count response statuses
        num_correct = sum(1 for r in responses if r.get('status') == 'Correct')
        num_partial = sum(1 for r in responses if r.get('status') == 'Partial')
        num_incorrect = sum(1 for r in responses if r.get('status') == 'Incorrect')
        
        return {
            'total_score': total_earned,
            'max_possible_score': total_possible,
            'score_percentage': (total_earned / total_possible * 100) if total_possible > 0 else 0,
            'num_correct': num_correct,
            'num_partial': num_partial,
            'num_incorrect': num_incorrect,
            'accuracy_rate': (num_correct / len(responses) * 100) if responses else 0
        }
    
    def _extract_typing_features(self, typing_metrics: Dict) -> Dict:
        """Extract typing pattern features"""
        return {
            'typing_speed_wpm': typing_metrics.get('avg_speed_wpm', 0),
            'typing_error_rate': typing_metrics.get('error_rate', 0),
            'typing_consistency': typing_metrics.get('consistency_score', 0),
            'typing_variability': typing_metrics.get('wpm_variability', 0),
            'total_typing_time': typing_metrics.get('total_time', 0)
        }
    
    def _extract_behavioral_features(self, responses: List[Dict]) -> Dict:
        """Extract behavioral markers from responses"""
        if not responses:
            return {
                'avg_response_length': 0,
                'response_length_variability': 0,
                'empty_response_count': 0
            }
        
        # Response lengths
        response_lengths = [len(r.get('user_answer', '')) for r in responses]
        
        # Count empty or very short responses (potential attention issues)
        empty_count = sum(1 for r in responses if len(r.get('user_answer', '').strip()) < 2)
        
        return {
            'avg_response_length': np.mean(response_lengths) if response_lengths else 0,
            'response_length_variability': np.std(response_lengths) if response_lengths else 0,
            'empty_response_count': empty_count,
            'empty_response_rate': (empty_count / len(responses) * 100) if responses else 0
        }
    
    def _extract_domain_features(self, responses: List[Dict]) -> Dict:
        """Extract domain-specific cognitive scores"""
        import pandas as pd
        
        if not responses:
            return {}
        
        df = pd.DataFrame(responses)
        
        # Group by cognitive domain
        domain_scores = {}
        if 'domain' in df.columns:
            for domain in df['domain'].unique():
                domain_data = df[df['domain'] == domain]
                earned = domain_data['earned'].sum()
                possible = domain_data['max_points'].sum()
                score_pct = (earned / possible * 100) if possible > 0 else 0
                
                # Clean domain name for feature key
                domain_key = domain.lower().replace(' ', '_').replace('&', 'and')
                domain_scores[f'domain_{domain_key}_score'] = score_pct
        
        return domain_scores
    
    def _extract_temporal_features(self, responses: List[Dict]) -> Dict:
        """Extract temporal patterns from response times"""
        if not responses:
            return {
                'avg_response_time': 0,
                'response_time_trend': 0
            }
        
        # Get response times (if tracked)
        response_times = [r.get('time_taken', 0) for r in responses]
        
        # Calculate trend (are they getting slower? - fatigue indicator)
        if len(response_times) > 2:
            # Simple linear trend
            x = np.arange(len(response_times))
            trend = np.polyfit(x, response_times, 1)[0] if len(response_times) > 1 else 0
        else:
            trend = 0
        
        return {
            'avg_response_time': np.mean(response_times) if response_times else 0,
            'response_time_variability': np.std(response_times) if response_times else 0,
            'response_time_trend': trend,  # Positive = getting slower (fatigue)
            'max_response_time': max(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0
        }
    
    def _extract_metadata_features(self, metadata: Dict) -> Dict:
        """Extract features from session metadata"""
        return {
            'age': metadata.get('age', 0),
            'education_years': metadata.get('education_years', 0),
            'has_prior_assessment': 1 if metadata.get('prior_assessment') else 0
        }
    
    def get_feature_vector(self, features: Dict) -> np.ndarray:
        """Convert feature dictionary to numpy array for ML model input"""
        # Ensure consistent ordering
        if not self.feature_names:
            self.feature_names = sorted(features.keys())
        
        return np.array([features.get(name, 0) for name in self.feature_names])
    
    def normalize_features(self, features: Dict) -> Dict:
        """Normalize features to 0-1 range for ML model"""
        normalized = features.copy()
        
        # Define normalization ranges for key features
        normalization_ranges = {
            'score_percentage': (0, 100),
            'typing_speed_wpm': (0, 80),
            'typing_error_rate': (0, 50),
            'typing_consistency': (0, 100),
            'age': (18, 100),
            'education_years': (0, 25)
        }
        
        for key, (min_val, max_val) in normalization_ranges.items():
            if key in normalized:
                value = normalized[key]
                normalized[f'{key}_normalized'] = np.clip((value - min_val) / (max_val - min_val), 0, 1)
        
        return normalized
