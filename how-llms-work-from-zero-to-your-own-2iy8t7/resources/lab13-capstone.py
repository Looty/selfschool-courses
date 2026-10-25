"""Lab 13 / capstone (chapter 13): train a bigger mini-GPT end to end, then judge it honestly.

Setup:  as lab 8 (torch, input.txt, minigpt.py)
Run:    python lab13-capstone.py                 (default config, about 5 to 10 minutes on a laptop CPU)
        python lab13-capstone.py 4 128 3000      (n_layer n_embd steps: change one thing at a time)
Writes: capstone-report.txt with your numbers, so you can compare runs.
"""
import sys

import torch

from minigpt import Config, Data, MiniGPT, n_params, sample_text, train

n_layer, n_embd, steps = (int(a) for a in sys.argv[1:4]) if len(sys.argv) >= 4 else (4, 128, 3000)
torch.manual_seed(7)
data = Data("input.txt")
cfg = Config(block_size=128, n_layer=n_layer, n_head=4, n_embd=n_embd)
model = MiniGPT(len(data.chars), cfg)
print(f"config: {cfg}\nparameters: {n_params(model):,}")

final = train(model, data, steps=steps, lr=2e-3, log_every=max(steps // 6, 1))

lines = [f"layers={n_layer} embd={n_embd} steps={steps} params={n_params(model):,} valid_loss={final:.3f}"]
for temperature in (0.5, 0.8, 1.2):
    text = sample_text(model, data, prompt="ROMEO:", n=250, temperature=temperature)
    lines.append(f"\n--- temperature {temperature} ---\n{text}")
report = "\n".join(lines)
print("\n" + report)
open("capstone-report.txt", "w", encoding="utf-8").write(report)
print("\nsaved capstone-report.txt")
