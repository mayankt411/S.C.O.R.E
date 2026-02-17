# Project Brief: S.C.O.R.E
### Systematic Cognitive Observation and Recognition Engine

S.C.O.R.E is a state-of-the-art, multi-modal cognitive assessment platform designed to modernize and enhance traditional MMSE (Mini-Mental State Examination) methodologies. By integrating deep semantic analysis, behavioral biometrics, and ensemble machine learning, the system provides clinical-grade neurocognitive insights with high precision.

## 🚀 Core Architecture
The system is built on a high-performance **FastAPI** backend, enabling asynchronous processing for real-time biometrics and AI inference.

### 1. Advanced Scoring Engine (SBERT)
Traditional assessment tools rely on literal string matching. S.C.O.R.E implements a **Neural Semantic Scoring Engine**:
- **Model**: `Sentence-BERT (all-MiniLM-L6-v2)`.
- **Capability**: Computes cosine similarity between user responses and clinical benchmarks, allowing for natural linguistic variation and partial credit navigation.
- **Logic**: Supports exact matches, semantic similarity (threshold-based), sequence patterns (counting tasks), and multi-word correction logic.

### 2. Behavioral Biometrics (Typing Dynamics)
Going beyond "what" is typed, the system analyzes "how" it is typed to detect early motor-cognitive decline:
- **Temporal Analysis (LSTM)**: A simulated Long Short-Term Memory network tracks fluctuations in keystroke timing to identify hesitation or cognitive load.
- **Anomaly Detection (Autoencoders)**: A simulated Deep Autoencoder maps typing patterns into a latent space, detecting deviations from "healthy" biometric signatures.
- **Metrics**: Real-time tracking of Words Per Minute (WPM), error rates (substitution, omission, addition, transposition), and rhythm consistency.

### 3. Disease Prediction & Explainability (Ensemble ML)
A sophisticated diagnostic pipeline categorizes cognitive health based on aggregated session data:
- **Models**: Ensemble of **XGBoost** and **Random Forest** classifiers.
- **Explainable AI (SHAP)**: Utilizes SHAP values to provide feature importance, showing clinicians exactly which domains (memory, orientation, motor speed) contributed to the risk prediction.
- **Hybrid Heuristics**: Combines ML predictions with rule-based clinical thresholds (MMSE-30 scale) for high-reliability results.

## 📊 UI/UX & Clinical Dashboard
The interface is designed for maximum engagement and clarity:
- **Visual Excellence**: Vibrant, high-contrast design using HSL color tokens, glassmorphism, and hardware-accelerated micro-animations.
- **Real-Time Analytics**: 
    - **Cognitive Radar Map**: Visualizes performance across Orientation, Memory, Attention, Language, and Executive Function.
    - **Typing Stability Graphs**: Live Plotly/Chart.js visualizations of behavioral biometrics.
- **Clinical Reporting**:
    - **FHIR Export**: Generates HL7 FHIR-compliant JSON bundles for seamless EHR (Electronic Health Record) integration.
    - **PDF Generation**: Automated PDF reports using `ReportLab`, including AI diagnostic summaries and response logs.

## 🏗️ Technical Stack
- **Backend**: FastAPI, Pydantic v2, Uvicorn.
- **AI/ML**: Scikit-learn, XGBoost, SHAP, Sentence-Transformers (SBERT).
- **Data/Math**: NumPy, Pandas.
- **Frontend**: Vanilla HTML5, Modern CSS3 (Variables, Flexbox/Grid), JavaScript (ES6+), Chart.js.
- **Reporting**: ReportLab (PDF), JSON (FHIR).

---
*Note: This system is currently configured for research and demonstration purposes. Clinical validation is required for diagnostic use.*
