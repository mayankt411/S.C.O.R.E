import datetime

def get_dynamic_questions():
    now = datetime.datetime.now()
    current_year = str(now.year)
    current_month = now.strftime("%B")
    current_day = str(now.day)
    day_of_week = now.strftime("%A")
    
    def get_season(month):
        if 3 <= month <= 5: return 'Spring'
        if 6 <= month <= 8: return 'Summer'
        if 9 <= month <= 11: return 'Fall'
        return 'Winter'
    current_season = get_season(now.month)

    return [
        # --- PHASE 1: ORIENTATION (Traditional) ---
        {
            "id": "q1_year",
            "domain": "Orientation",
            "text": "What is the current year?",
            "expected_answers": [current_year, "2026"],
            "type": "exact_or_semantic",
            "points": 1,
            "input_type": "text"
        },
        
        # --- PHASE 2: SPECIALIZED TEXT & ERROR DETECTION (Project Brief Step 1) ---
        {
            "id": "q2_error_detection",
            "domain": "Visual & Language Analysis",
            "text": "Type the word 'Pneumonia' exactly. Then type the following word correctly: 'Alzheimerrs' (it has an error at the end).",
            "expected_answers": ["Pneumonia Alzheimer"],
            "type": "multi_word_correction",
            "points": 2,
            "input_type": "text",
            "description": "Tests ability to identify and correct errors in terminal positions."
        },
        {
            "id": "q3_repeated_words",
            "domain": "Focus & Discrimination",
            "text": "Below are two versions of a word. Type ONLY the correctly spelled one: 'Hospital' or 'Hospitall'?",
            "expected_answers": ["Hospital"],
            "type": "exact",
            "points": 1,
            "input_type": "text"
        },
        {
            "id": "q4_long_short",
            "domain": "Linguistic Complexity",
            "text": "Type these three words in sequence, separated by spaces: 'Cat', 'Hippopotamus', 'Incomprehensibility'.",
            "expected_answers": ["Cat Hippopotamus Incomprehensibility"],
            "type": "exact",
            "points": 3,
            "input_type": "text"
        },
        
        {
            "id": "q5_orientation_location",
            "domain": "Orientation",
            "text": "What is the name of the city and state you are in right now?",
            "expected_answers": [], # Scored by presence of data/length or semantic check if location known
            "type": "data_collection",
            "points": 2,
            "input_type": "text"
        },

        # --- PHASE 4: MEMORY ENCODING ---
        {
            "id": "q6_memory_encoding",
            "domain": "Memory Encoding",
            "text": "Memorize these 3 words clearly. I will ask you for them later.",
            "content": ["VELOCITY", "HORIZON", "QUANTUM"],
            "expected_answers": ["VELOCITY HORIZON QUANTUM"],
            "type": "display_only",
            "points": 0,
            "input_type": "button",
            "button_text": "I have memorized them"
        },

        # --- PHASE 5: ATTENTION & CALCULATION ---
        {
            "id": "q7_attention",
            "domain": "Attention & Calculation",
            "text": "Start at 100 and count backwards by 7. Type the first 5 numbers (e.g., 93 86...)",
            "expected_answers": ["93 86 79 72 65"],
            "type": "sequence",
            "points": 5,
            "input_type": "text"
        },

        # --- PHASE 6: DELAYED RECALL ---
        {
            "id": "q8_recall",
            "domain": "Recall",
            "text": "What were the 3 words you memorized earlier?",
            "expected_answers": ["VELOCITY", "HORIZON", "QUANTUM"],
            "type": "multi_match",
            "points": 3,
            "input_type": "text"
        },

        # --- PHASE 7: REPETITION (Traditional MMSE) ---
        {
            "id": "q9_repetition",
            "domain": "Language Analysis",
            "text": "Type the following phrase exactly: 'No ifs, ands, or buts'.",
            "expected_answers": ["No ifs, ands, or buts", "No ifs ands or buts"],
            "type": "exact_or_semantic",
            "points": 2,
            "input_type": "text"
        },
        
        # --- PHASE 8: EXECUTIVE LOGIC ---
        {
            "id": "q10_logic",
            "domain": "Executive Function",
            "text": "If you have an apple and you take away half, how much apple do you have left?",
            "expected_answers": ["half", "0.5", "50%", "one half", "a half"],
            "type": "semantic_reasoning",
            "points": 1,
            "input_type": "text"
        }
    ]

