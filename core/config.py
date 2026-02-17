import os

# --- APP SETTINGS ---
APP_TITLE = "S.C.O.R.E"
APP_SUBTITLE = "Systematic Cognitive Observation and Recognition Engine"

# --- VIBRANT COLOR PALETTE ---
# Primary Colors (Vibrant Gradient)
COLOR_PRIMARY = "#6366f1"  # Vibrant Indigo
COLOR_PRIMARY_DARK = "#4f46e5"
COLOR_PRIMARY_LIGHT = "#818cf8"
COLOR_SECONDARY = "#ec4899"  # Vibrant Pink
COLOR_ACCENT = "#14b8a6"  # Vibrant Teal

# Semantic Colors
COLOR_SUCCESS = "#10b981"  # Vibrant Green
COLOR_WARNING = "#f59e0b"  # Vibrant Amber
COLOR_DANGER = "#ef4444"  # Vibrant Red
COLOR_INFO = "#3b82f6"  # Vibrant Blue

# Neutral Colors (High Contrast for Readability)
COLOR_TEXT_PRIMARY = "#0f172a"  # Slate 900
COLOR_TEXT_SECONDARY = "#475569"  # Slate 600
COLOR_TEXT_MUTED = "#64748b"  # Slate 500
COLOR_BACKGROUND = "#ffffff"
COLOR_BACKGROUND_SECONDARY = "#f8fafc"  # Slate 50
COLOR_BORDER = "#e2e8f0"  # Slate 200

# Gradient Definitions
GRADIENT_PRIMARY = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
GRADIENT_SUCCESS = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
GRADIENT_DANGER = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
GRADIENT_HERO = "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"

# --- TYPOGRAPHY ---
FONT_FAMILY_PRIMARY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
FONT_FAMILY_MONO = "'JetBrains Mono', 'Fira Code', 'Courier New', monospace"

FONT_SIZE_XS = "0.75rem"
FONT_SIZE_SM = "0.875rem"
FONT_SIZE_BASE = "1rem"
FONT_SIZE_LG = "1.125rem"
FONT_SIZE_XL = "1.25rem"
FONT_SIZE_2XL = "1.5rem"
FONT_SIZE_3XL = "1.875rem"
FONT_SIZE_4XL = "2.25rem"

# --- ANIMATION SETTINGS ---
ANIMATION_DURATION_FAST = "150ms"
ANIMATION_DURATION_BASE = "300ms"
ANIMATION_DURATION_SLOW = "500ms"
ANIMATION_EASING = "cubic-bezier(0.4, 0, 0.2, 1)"

# --- SCORING SETTINGS ---
# Thresholds for Semantic Similarity (Cosine Similarity)
THRESHOLD_EXACT = 0.95      # Treated as 100% correct
THRESHOLD_PARTIAL = 0.75    # Treated as 50% partial credit
THRESHOLD_MIN = 0.50        # Below this is 0%

# Error Type Weights
ERROR_WEIGHT_TRANSPOSITION = 0.3
ERROR_WEIGHT_SUBSTITUTION = 0.5
ERROR_WEIGHT_OMISSION = 0.4
ERROR_WEIGHT_ADDITION = 0.4

# --- MODEL SETTINGS ---
# Sentence-BERT Model (Small, fast, effective)
SBERT_MODEL_NAME = 'all-MiniLM-L6-v2'

# LLM Settings (OpenAI)
OPENAI_MODEL = "gpt-3.5-turbo"
ENABLE_LLM_SCORING = True  # Set to False to disable LLM UI toggle

# --- DISEASE PREDICTION SETTINGS ---
ENABLE_DISEASE_PREDICTION = True
ENABLE_TYPING_ANALYSIS = True

# MMSE Score Thresholds (Traditional)
MMSE_THRESHOLD_NORMAL = 24
MMSE_THRESHOLD_MILD = 18
MMSE_THRESHOLD_MODERATE = 10

# Typing Speed Benchmarks (Words Per Minute by age group)
TYPING_SPEED_NORMAL_YOUNG = 40  # 18-40 years
TYPING_SPEED_NORMAL_MIDDLE = 35  # 41-65 years
TYPING_SPEED_NORMAL_SENIOR = 25  # 65+ years

# Error Rate Thresholds (percentage)
ERROR_RATE_NORMAL = 5
ERROR_RATE_MILD = 15
ERROR_RATE_MODERATE = 30

# --- PATHS ---
DATA_DIR = "data"
REPORTS_DIR = "reports"
MODELS_DIR = "ml_models/saved_models"

# --- PROMPTS ---
LLM_SYSTEM_PROMPT = """
You are an expert cognitive assessment scorer. 
Your task is to evaluate a user's text response against a ground truth answer.
You must consider:
1. Semantic meaning (does it mean the same thing?)
2. Context (is it appropriate for the question?)
3. Spelling/Grammar (minor errors are okay, major are not)

Return a valid JSON object with:
- score (0.0 to 1.0)
- reasoning (brief explanation)
- feedback (constructive feedback for the user)
"""

# --- DISEASE CATEGORIES ---
DISEASE_TYPES = [
    "Healthy/Normal",
    "Mild Cognitive Impairment (MCI)",
    "Alzheimer's Disease",
    "Vascular Dementia",
    "Parkinson's Disease",
    "Frontotemporal Dementia",
    "Lewy Body Dementia"
]

SEVERITY_STAGES = [
    "Normal",
    "Mild Cognitive Impairment",
    "Mild Impairment",
    "Moderate Impairment",
    "Severe Impairment"
]
