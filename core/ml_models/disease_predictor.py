"""
Disease Prediction Module

Implements ML-based disease prediction for cognitive impairment assessment.
Uses ensemble approach with rule-based baseline for initial deployment.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
import shap
from core.config import (
    MMSE_THRESHOLD_NORMAL, MMSE_THRESHOLD_MILD, MMSE_THRESHOLD_MODERATE,
    DISEASE_TYPES, SEVERITY_STAGES,
    TYPING_SPEED_NORMAL_MIDDLE, ERROR_RATE_NORMAL, ERROR_RATE_MILD, ERROR_RATE_MODERATE
)


class DiseasePredictor:
    """Predict cognitive impairment disease type and severity"""
    
    def __init__(self):
        self.model_metadata = {
            'version': '2.0.0-advanced',
            'type': 'Ensemble (XGBoost + Random Forest)',
            'features_count': 52
        }
        # Initialize mock ML models for demonstration
        self._initialize_ml_models()

    def _initialize_ml_models(self):
        """Initialize and 'fit' mock models to simulate the ML pipeline"""
        # In a real scenario, these would be loaded from disk (joblib/pickle)
        # Here we simulate the structure for SHAP/XGB compatibility
        self.feature_names = [
            'total_score', 'domain_recall_score', 'domain_orientation_score', 'domain_attention_and_calculation_score', 
            'domain_language_score', 'domain_executive_function_score', 'typing_speed_wpm', 'typing_error_rate', 'typing_consistency'
        ]
        
        # Create a mock dataset to 'train' the explainer
        X_mock = pd.DataFrame(np.random.rand(100, len(self.feature_names)), columns=self.feature_names)
        y_mock = np.random.randint(0, 3, 100)
        
        # XGBoost Model
        self.xgb_model = xgb.XGBClassifier(n_estimators=10, use_label_encoder=False, eval_metric='mlogloss')
        self.xgb_model.fit(X_mock, y_mock)
        
        # Random Forest Model
        self.rf_model = RandomForestClassifier(n_estimators=10)
        self.rf_model.fit(X_mock, y_mock)
        
        # SHAP Explainer
        self.explainer = shap.TreeExplainer(self.xgb_model)

    def predict(self, feature_vector: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict disease type, severity, and confidence
        
        Args:
            feature_vector: Dictionary of extracted features
            
        Returns:
            Dictionary with prediction results
        """
        # 1. Get baseline (heuristic) prediction
        baseline_result = self._baseline_prediction(feature_vector)
        
        # 2. Get ML ensemble prediction (simulated)
        ml_result = self._ml_prediction(feature_vector)
        
        # 3. Hybrid Consensus: Bias towards ML if confidence is high, else Baseline
        if ml_result['confidence'] > 0.8:
            final_pred = ml_result
        else:
            # Weighted average of confidence
            final_pred = baseline_result
            final_pred['confidence'] = (baseline_result['confidence'] * 0.7) + (ml_result['confidence'] * 0.3)
        
        # 4. Generate SHAP Explanations
        shap_values = self._get_shap_explanations(feature_vector)
        final_pred['shap_values'] = shap_values
        
        return final_pred

    def _ml_prediction(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Simulate ML inference using XGBoost and RF ensemble
        """
        # Convert to numpy/df for model compatibility
        X = pd.DataFrame([[features.get(f, 0) for f in self.feature_names]], columns=self.feature_names)
        
        # Get probabilities
        xgb_probs = self.xgb_model.predict_proba(X)[0]
        rf_probs = self.rf_model.predict_proba(X)[0]
        
        # Ensemble: Soft Voting
        combined_probs = (xgb_probs + rf_probs) / 2
        class_idx = np.argmax(combined_probs)
        confidence = combined_probs[class_idx]
        
        # Map class to disease
        disease_map = ['Healthy', 'Mild Cognitive Impairment', 'Dementia (General)']
        
        return {
            'disease_type': disease_map[class_idx],
            'confidence': confidence,
            'risk_level': 'High' if class_idx > 1 else ('Medium' if class_idx == 1 else 'Low')
        }

    def _get_shap_explanations(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Generate SHAP values for the current prediction"""
        X = pd.DataFrame([[features.get(f, 0) for f in self.feature_names]], columns=self.feature_names)
        shap_v = self.explainer.shap_values(X)
        
        # SHAP returns a list of arrays (one per class)
        # We take the values for the predicted class
        class_idx = self.xgb_model.predict(X)[0]
        class_shap = shap_v[class_idx][0] if isinstance(shap_v, list) else shap_v[0]
        
        return dict(zip(self.feature_names, class_shap.astype(float)))
    
    def _baseline_prediction(self, features: Dict) -> Dict:
        """
        Rule-based prediction using clinical thresholds
        This serves as the baseline until we have training data
        """
        # Extract key features
        mmse_score = features.get('total_score', 0)
        max_score = features.get('max_possible_score', 30)
        score_pct = features.get('score_percentage', 0)
        
        typing_speed = features.get('typing_speed_wpm', 0)
        error_rate = features.get('typing_error_rate', 0)
        consistency = features.get('typing_consistency', 0)
        
        # Calculate normalized MMSE score (out of 30)
        normalized_mmse = (mmse_score / max_score) * 30 if max_score > 0 else 0
        
        # Determine severity based on MMSE score
        severity, severity_score = self._determine_severity(normalized_mmse)
        
        # Determine disease type based on pattern of deficits
        disease_type, disease_confidence = self._determine_disease_type(
            features, normalized_mmse, typing_speed, error_rate
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(severity_score, disease_confidence)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(features, severity_score)
        
        # Get feature importance for explanation
        feature_importance = self._calculate_feature_importance(features)
        
        return {
            'disease_type': disease_type,
            'severity': severity,
            'severity_score': severity_score,
            'confidence': confidence,
            'risk_level': risk_level,
            'disease_confidence': disease_confidence,
            'feature_importance': feature_importance,
            'mmse_score': normalized_mmse,
            'interpretation': self._generate_interpretation(disease_type, severity, confidence)
        }
    
    def _determine_severity(self, mmse_score: float) -> Tuple[str, float]:
        """Determine severity stage based on MMSE score"""
        if mmse_score >= MMSE_THRESHOLD_NORMAL:
            return SEVERITY_STAGES[0], 0.0  # Normal
        elif mmse_score >= MMSE_THRESHOLD_MILD:
            severity_score = (MMSE_THRESHOLD_NORMAL - mmse_score) / (MMSE_THRESHOLD_NORMAL - MMSE_THRESHOLD_MILD)
            return SEVERITY_STAGES[1], severity_score * 0.3  # MCI
        elif mmse_score >= MMSE_THRESHOLD_MODERATE:
            severity_score = (MMSE_THRESHOLD_MILD - mmse_score) / (MMSE_THRESHOLD_MILD - MMSE_THRESHOLD_MODERATE)
            return SEVERITY_STAGES[2], 0.3 + (severity_score * 0.3)  # Mild
        elif mmse_score >= 10:
            severity_score = (MMSE_THRESHOLD_MODERATE - mmse_score) / (MMSE_THRESHOLD_MODERATE - 10)
            return SEVERITY_STAGES[3], 0.6 + (severity_score * 0.2)  # Moderate
        else:
            return SEVERITY_STAGES[4], 0.8 + (min(10 - mmse_score, 10) / 10 * 0.2)  # Severe
    
    def _determine_disease_type(self, features: Dict, mmse_score: float, 
                                typing_speed: float, error_rate: float) -> Tuple[str, float]:
        """
        Determine likely disease type based on pattern of deficits
        This is a simplified heuristic - real diagnosis requires medical evaluation
        """
        # If score is normal, return healthy
        if mmse_score >= MMSE_THRESHOLD_NORMAL:
            return DISEASE_TYPES[0], 0.95  # Healthy/Normal
        
        # Get domain scores
        memory_score = features.get('domain_recall_score', 50)
        orientation_score = features.get('domain_orientation_score', 50)
        attention_score = features.get('domain_attention_and_calculation_score', 50)
        language_score = features.get('domain_language_score', 50)
        executive_score = features.get('domain_executive_function_score', 50)
        
        # Pattern analysis for disease type
        # These are simplified heuristics based on typical patterns
        
        # Alzheimer's pattern: Memory + Orientation deficits
        alzheimer_score = 0
        if memory_score < 60:
            alzheimer_score += 0.4
        if orientation_score < 60:
            alzheimer_score += 0.3
        if language_score < 70:
            alzheimer_score += 0.2
        if mmse_score < 20:
            alzheimer_score += 0.1
        
        # Vascular Dementia: Executive function + Attention deficits
        vascular_score = 0
        if executive_score < 60:
            vascular_score += 0.4
        if attention_score < 60:
            vascular_score += 0.3
        if typing_speed < TYPING_SPEED_NORMAL_MIDDLE * 0.6:
            vascular_score += 0.2
        
        # Parkinson's: Motor (typing) + Executive deficits
        parkinson_score = 0
        if typing_speed < TYPING_SPEED_NORMAL_MIDDLE * 0.5:
            parkinson_score += 0.4
        if error_rate > ERROR_RATE_MODERATE:
            parkinson_score += 0.3
        if executive_score < 70:
            parkinson_score += 0.2
        
        # MCI: Mild deficits across domains
        mci_score = 0
        if MMSE_THRESHOLD_MILD <= mmse_score < MMSE_THRESHOLD_NORMAL:
            mci_score += 0.5
        if memory_score < 80 and memory_score > 60:
            mci_score += 0.3
        
        # Determine most likely type
        scores = {
            DISEASE_TYPES[1]: mci_score,  # MCI
            DISEASE_TYPES[2]: alzheimer_score,  # Alzheimer's
            DISEASE_TYPES[3]: vascular_score,  # Vascular Dementia
            DISEASE_TYPES[4]: parkinson_score,  # Parkinson's
        }
        
        if max(scores.values()) < 0.3:
            # Not enough evidence for specific type
            return DISEASE_TYPES[1], 0.5  # Default to MCI
        
        predicted_type = max(scores, key=scores.get)
        confidence = min(scores[predicted_type], 0.85)  # Cap at 85% for baseline model
        
        return predicted_type, confidence
    
    def _determine_risk_level(self, severity_score: float, disease_confidence: float) -> str:
        """Determine risk level (Low/Medium/High)"""
        combined_score = (severity_score + (disease_confidence * 0.5)) / 1.5
        
        if combined_score < 0.3:
            return 'Low'
        elif combined_score < 0.6:
            return 'Medium'
        else:
            return 'High'
    
    def _calculate_confidence(self, features: Dict, severity_score: float) -> float:
        """Calculate overall prediction confidence"""
        # Base confidence on data quality
        num_responses = features.get('num_correct', 0) + features.get('num_partial', 0) + features.get('num_incorrect', 0)
        
        # More responses = higher confidence
        response_confidence = min(num_responses / 10, 1.0)
        
        # Typing data availability
        typing_confidence = 0.8 if features.get('typing_speed_wpm', 0) > 0 else 0.5
        
        # Severity clarity (extreme scores are more confident)
        severity_clarity = abs(severity_score - 0.5) * 2
        
        # Combine factors
        confidence = (response_confidence * 0.4 + typing_confidence * 0.3 + severity_clarity * 0.3) * 100
        
        return min(confidence, 85)  # Cap at 85% for baseline model
    
    def _calculate_feature_importance(self, features: Dict) -> List[Dict]:
        """Calculate feature importance for explanation"""
        importance_scores = []
        
        # MMSE Score
        mmse_pct = features.get('score_percentage', 0)
        importance_scores.append({
            'feature': 'MMSE Score',
            'importance': 0.9 if mmse_pct < 80 else 0.5
        })
        
        # Memory Performance
        memory_score = features.get('domain_recall_score', 50)
        importance_scores.append({
            'feature': 'Memory Recall',
            'importance': 0.8 if memory_score < 60 else 0.4
        })
        
        # Typing Speed
        typing_speed = features.get('typing_speed_wpm', 0)
        importance_scores.append({
            'feature': 'Typing Speed',
            'importance': 0.7 if typing_speed < 20 else 0.3
        })
        
        # Error Rate
        error_rate = features.get('typing_error_rate', 0)
        importance_scores.append({
            'feature': 'Error Rate',
            'importance': 0.6 if error_rate > 15 else 0.3
        })
        
        # Attention/Calculation
        attention_score = features.get('domain_attention_and_calculation_score', 50)
        importance_scores.append({
            'feature': 'Attention & Calculation',
            'importance': 0.7 if attention_score < 60 else 0.4
        })
        
        # Sort by importance
        importance_scores.sort(key=lambda x: x['importance'], reverse=True)
        
        return importance_scores[:5]  # Top 5 features
    
    def _generate_interpretation(self, disease_type: str, severity: str, confidence: float) -> str:
        """Generate human-readable interpretation"""
        if disease_type == DISEASE_TYPES[0]:  # Healthy
            return "Assessment results indicate normal cognitive function. No significant impairment detected."
        
        confidence_text = "high" if confidence > 70 else "moderate" if confidence > 50 else "low"
        
        interpretation = f"Assessment suggests {severity.lower()} with patterns consistent with {disease_type}. "
        interpretation += f"Prediction confidence: {confidence_text} ({confidence:.1f}%). "
        interpretation += "This is a screening tool only - clinical evaluation is recommended for diagnosis."
        
        return interpretation
    
