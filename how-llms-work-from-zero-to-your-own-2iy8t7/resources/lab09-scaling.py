"""Lab 9 (chapter 9): see a scaling law in miniature. Train three sizes of mini-GPT and compare.

Setup:  as lab 8 (torch, input.txt, minigpt.py)
Run:    python lab09-scaling.py        (about 3 to 5 minutes on a laptop CPU)
Question to ask yourself: does a bigger model give lower loss for the same number of training steps?
"""
import torch

from minigpt import Config, Data, MiniGPT, n_params, train

data = Data("input.txt")
STEPS = 600
rows = []
for n_embd in (16, 32, 64):
    torch.manual_seed(0)
    model = MiniGPT(len(data.chars), Config(n_embd=n_embd, n_head=4))
    print(f"\n=== n_embd={n_embd}: {n_params(model):,} parameters ===")
    loss = train(model, data, steps=STEPS, log_every=STEPS)
    rows.append((n_params(model), loss))

print("\nparameters   validation loss")
for p, l in rows:
    print(f"{p:>10,}   {l:.3f}")
print("\nEach model saw the same amount of text. In the scaling-law papers, loss falls as a smooth power law as models and data grow.")
