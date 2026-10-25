"""Lab 1 (chapter 1): make a real language model continue a sentence, on your own machine.

Setup:  uv venv && uv pip install torch transformers
Run:    python lab01-gpt2-chat.py "The capital of France is"
Needs a one-time download of the small GPT-2 model (about 0.5 GB) from Hugging Face; after that it works offline.
"""
import sys

from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

sys.stdout.reconfigure(encoding="utf-8")  # GPT-2 marks a leading space with the character 'Ġ'; Windows consoles choke on it
prompt = sys.argv[1] if len(sys.argv) > 1 else "The capital of France is"
set_seed(42)

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")

inputs = tokenizer(prompt, return_tensors="pt")
print("tokens the model sees:", tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]))

for do_sample, label in [(False, "greedy (always the most likely next token)"), (True, "sampled (temperature 0.9)")]:
    out = model.generate(
        **inputs,
        max_new_tokens=30,  # the default is only 20 new tokens
        do_sample=do_sample,
        temperature=0.9 if do_sample else None,
        pad_token_id=tokenizer.eos_token_id,
    )
    print(f"\n--- {label} ---")
    print(tokenizer.decode(out[0], skip_special_tokens=True))
