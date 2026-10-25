"""Lab 8 (chapter 8): train a tiny GPT on your CPU and watch it learn to write.

Setup:  uv venv && uv pip install torch numpy ; python lab-corpus.py
Run:    python lab08-train-mini-gpt.py            (1000 steps: about 1 minute on a laptop CPU)
Then:   python lab08-train-mini-gpt.py 4000       (more steps, lower loss, better text)
Needs:  minigpt.py and input.txt in the same folder.
"""
import sys

import torch

from minigpt import Config, Data, MiniGPT, n_params, sample_text, train

torch.manual_seed(1337)
data = Data("input.txt")
model = MiniGPT(len(data.chars), Config())
print(f"{len(data.chars)} characters in the vocabulary, {n_params(model):,} parameters")

print("\n--- before training (random weights) ---")
print(sample_text(model, data, n=150))

steps = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
final = train(model, data, steps=steps, log_every=max(steps // 4, 1))

print("\n--- after training ---")
print(sample_text(model, data, n=400))
print(f"\nfinal validation loss {final:.3f}")
torch.save(model.state_dict(), "mini-gpt.pt")
print("saved mini-gpt.pt")
