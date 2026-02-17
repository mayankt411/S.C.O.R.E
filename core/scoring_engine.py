import numpy as np
from difflib import SequenceMatcher
try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None

from core.config import THRESHOLD_EXACT, THRESHOLD_PARTIAL, THRESHOLD_MIN, SBERT_MODEL_NAME

class ScoringEngine:
    _model_instance = None

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Lazy load SBERT model to avoid startup temp hang."""
        if SentenceTransformer:
            try:
                if ScoringEngine._model_instance is None:
                    print(f"Loading AI Model ({SBERT_MODEL_NAME})...")
                    ScoringEngine._model_instance = SentenceTransformer(SBERT_MODEL_NAME)
                self.model = ScoringEngine._model_instance
            except Exception as e:
                print(f"Failed to load SBERT: {e}")
                self.model = None

    def calculate_similarity(self, text1, text2):
        """Returns cosine similarity between two strings (0.0 to 1.0)."""
        if not self.model:
            # Fallback to SequenceMatcher if model fails
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
            
        # Compute embeddings
        embeddings1 = self.model.encode(text1, convert_to_tensor=True)
        embeddings2 = self.model.encode(text2, convert_to_tensor=True)
        
        # Cosine similarity
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        return float(cosine_scores[0][0])

    def score(self, user_ans, expected_answers, q_type="semantic"):
        """
        Main scoring routing.
        params:
            user_ans: str
            expected_answers: list[str]
            q_type: str (semantic, exact, multi_match, sequence, etc)
        returns: (score_float, status_str, feedback_str)
        """
        if not user_ans or not user_ans.strip():
            return 0.0, "Missing", "No answer provided."

        user_ans = user_ans.strip()
        
        # --- Type: Display Only ---
        if q_type == "display_only":
            return 1.0, "Info", "Task completed."

        # --- Type: Data Collection (Personal Info) ---
        if q_type == "data_collection":
            # Give points for providing enough info (e.g. at least 2 words)
            words = user_ans.split()
            if len(words) >= 2:
                return 1.0, "Correct", "Information captured successfully."
            elif len(words) > 0:
                return 0.5, "Partial", "Partial information provided."
            return 0.0, "Incorrect", "Information missing."

        # --- Type: Sequence (Math/Counting) ---
        if q_type == "sequence":
            target = expected_answers[0].replace(',', ' ').split()
            user = user_ans.replace(',', ' ').split()
            
            correct_count = 0
            for i, val in enumerate(target):
                if i < len(user) and user[i] == val:
                    correct_count += 1
            
            score = correct_count / len(target)
            status = "Correct" if score == 1.0 else "Partial" if score > 0 else "Incorrect"
            return score, status, f"Correctly identified {correct_count}/{len(target)} in sequence."

        # --- Type: Multi Word Correction ---
        if q_type == "multi_word_correction":
            # e.g. "Pneumonia Alzheimer"
            target_words = expected_answers[0].lower().split()
            user_words = user_ans.lower().split()
            
            matches = 0
            for tw in target_words:
                best_sim = 0
                for uw in user_words:
                    sim = self.calculate_similarity(tw, uw)
                    if sim > best_sim: best_sim = sim
                if best_sim > 0.85: matches += 1
            
            score = matches / len(target_words)
            status = "Correct" if score == 1.0 else "Partial" if score > 0 else "Incorrect"
            return score, status, f"Matched {matches}/{len(target_words)} target words."

        # --- Type: Multi Match (Recall) ---
        if q_type == "multi_match":
            # Heuristic for multiple items (e.g. "Velocity Horizon Quantum")
            found_count = 0
            missing = []
            normalized_user = user_ans.lower()
            
            target_words = expected_answers if isinstance(expected_answers, list) else []
            if not target_words and expected_answers:
                target_words = str(expected_answers).split()

            total_items = len(target_words)
            if total_items == 0: return 0.0, "Error", "Config Error"

            for word in target_words:
                best_word_sim = 0.0
                for user_word in normalized_user.split():
                    sim = self.calculate_similarity(word.lower(), user_word)
                    if sim > best_word_sim:
                        best_word_sim = sim
                
                if best_word_sim > THRESHOLD_PARTIAL:
                    found_count += 1
                else:
                    missing.append(word)
            
            score = found_count / total_items
            feedback = f"Recalled {found_count}/{total_items} items."
            if missing:
                feedback += f" Missed: {', '.join(missing)}"
            
            status = "Correct" if score == 1.0 else "Partial" if score > 0 else "Incorrect"
            return score, status, feedback

        # --- Type: Standard Semantic / Exact ---
        best_sim = 0.0
        best_match_txt = ""

        for target in expected_answers:
            if q_type == "exact_case_sensitive":
                if user_ans == target:
                    best_sim = 1.0
                else:
                    sim = SequenceMatcher(None, user_ans, target).ratio()
                    if sim > 0.9: best_sim = 0.5 # Typo tolerance but reduced score
            
            elif q_type == "exact":
                if user_ans.lower() == target.lower():
                    best_sim = 1.0
                else:
                    sim = SequenceMatcher(None, user_ans.lower(), target.lower()).ratio()
                    if sim > 0.8: best_sim = 0.9 # High typo tolerance
            
            elif q_type == "exact_or_semantic":
                # Check exact first
                if user_ans.lower() == target.lower():
                    best_sim = 1.0
                else:
                    sim = self.calculate_similarity(user_ans, target)
                    if sim > best_sim: best_sim = sim
            
            else: # Semantic
                sim = self.calculate_similarity(user_ans, target)
                if sim > best_sim:
                    best_sim = sim
                    best_match_txt = target

        # Thresholding
        if best_sim >= THRESHOLD_EXACT:
            return 1.0, "Correct", "Excellent match."
        elif best_sim >= THRESHOLD_PARTIAL:
            return 0.5, "Partial", f"Close match logic ({int(best_sim*100)}%)."
        elif best_sim >= THRESHOLD_MIN:
            return 0.25, "Weak", f"Vague similarity detected ({int(best_sim*100)}%)."
        else:
            return 0.0, "Incorrect", f"Response mismatch ({int(best_sim*100)}%)."

# TODO: Add LLMScorer class here linking to OpenAI
class LLMScorer:
    def __init__(self, api_key=None):
        self.api_key = api_key
        
    def evaluate(self, question, user_ans, expected):
        # Placeholder for OpenAI call
        # In production this would use `openai.ChatCompletion.create`
        return 0.0, "LLM Disabled", "LLM scoring not yet configured."
