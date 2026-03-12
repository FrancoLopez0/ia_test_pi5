import ollama
import time
import re
import statistics

# --- CONFIG ---
MODEL_NAME = 'custom-llm-0.5b'
# Simplified English Stop Words
STOP_WORDS = {'please', 'i', 'want', 'you', 'to', 'the', 'with', 'at', 'a', 'of', 'and'}
# Direct English Mapping
SYNONYM_MAP = {
    'forward': 'FWD', 'backward': 'BWD', 'back': 'BWD',
    'right': 'RIGHT', 'left': 'LEFT',
    'stop': 'STOP', 'halt': 'STOP',
    'speed': 'VEL', 'power': 'VEL', 'fast': 'VEL_MAX'
}

TEST_CASES = [
    "Please move the motor to the right with power 80",
    "I want you to go backward with a speed of 50",
    "Stop immediately please",
    "Turn left very fast power 100"
]

# def preprocess_english(text: str) -> str:
#     """Standardizes input into a dense English DSL."""
#     clean = re.sub(r'[^\w\s]', '', text.lower())
#     words = [w for w in clean.split() if w not in STOP_WORDS]
#     normalized = [SYNONYM_MAP.get(w, w).upper() for w in words]
#     return " ".join(normalized)

def preprocess_for_coder(text: str) -> str:
    # No limpiamos nada, solo le damos contexto de código
    return f"Translate to python: {text}"

def run_english_benchmark():
    print(f"--- Running English Logic Benchmark (Pi 5) ---\n")
    
    raw_times, opt_times = [], []

    for i, raw_prompt in enumerate(TEST_CASES):
        # 1. RAW ENGLISH TEST
        t0 = time.time()
        # resp_raw = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': raw_prompt}])
        resp_raw = ollama.generate(
            model='custom-llm-0.5b',
            prompt=f"INPUT: {raw_prompt}\nOUTPUT:", # Prompt minimalista
            options={'num_predict': 5} # Limitamos la salida físicamente
        )
        t1 = time.time()
        raw_times.append(t1 - t0)

        # 2. OPTIMIZED ENGLISH TEST
        dense_prompt = preprocess_for_coder(raw_prompt)
        t2 = time.time()
        resp_opt = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': dense_prompt}])
        t3 = time.time()
        opt_times.append(t3 - t2)

        # DEBUG OUTPUTS
        print(f"Test {i+1}: '{raw_prompt}'")
        print(f"  [Raw] Time: {t1 - t0:.2f}s | Tokens In: {resp_raw['prompt_eval_count']} | Out: {resp_raw['eval_count']}")
        print(f"  [Opt] Time: {t3 - t2:.2f}s | Tokens In: {resp_opt['prompt_eval_count']} | Out: {resp_opt['eval_count']}")
        print(f"  [Response Opt]: {resp_opt['message']['content'].strip()}")
        print("-" * 30)

    # FINAL METRICS
    avg_raw, avg_opt = statistics.mean(raw_times), statistics.mean(opt_times)
    print(f"\nFINAL RESULTS:")
    print(f"Avg Raw Latency: {avg_raw:.3f}s")
    print(f"Avg Opt Latency: {avg_opt:.3f}s")
    print(f"Improvement: {((avg_raw - avg_opt) / avg_raw) * 100:.1f}%")

if __name__ == "__main__":
    run_english_benchmark()