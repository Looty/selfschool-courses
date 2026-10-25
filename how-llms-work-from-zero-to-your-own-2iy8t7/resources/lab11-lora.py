"""Lab 11 (chapter 11): LoRA by hand. Fine-tune your mini-GPT by training only a few new numbers.

Idea (Hu et al. 2021): freeze the pretrained weights W and learn a small correction B @ A, where A and B are
thin matrices. Instead of changing every number in W, you train two small matrices.
This is a teaching implementation of the idea, not the official LoRA library.

Setup:  as lab 8; run `python lab08-train-mini-gpt.py` first (it saves mini-gpt.pt)
Run:    python lab11-lora.py
"""
import torch
import torch.nn as nn

from minigpt import Config, Data, MiniGPT, eval_loss, n_params, sample_text, train


class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, rank: int = 4, alpha: float = 8.0):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False  # freeze the original weights
        self.A = nn.Parameter(torch.randn(rank, base.in_features) * 0.01)
        self.B = nn.Parameter(torch.zeros(base.out_features, rank))  # zeros: at the start the correction is nothing
        self.scale = alpha / rank

    def forward(self, x):
        return self.base(x) + (x @ self.A.T @ self.B.T) * self.scale


torch.manual_seed(0)
data = Data("input.txt")
model = MiniGPT(len(data.chars), Config())
model.load_state_dict(torch.load("mini-gpt.pt"))

# New task: write in ALL CAPITALS. Same characters, different "style".
text = open("input.txt", encoding="utf-8").read().upper()
caps = Data.__new__(Data)
caps.chars, caps.stoi = data.chars, data.stoi
ids = torch.tensor([data.stoi[c] for c in text if c in data.stoi], dtype=torch.long)
n = int(0.9 * len(ids))
caps.train, caps.valid = ids[:n], ids[n:]

print(f"loss on the new task before fine-tuning: {eval_loss(model, caps):.3f}")

total = n_params(model)
for blk in model.blocks:  # wrap the attention projections
    blk.attn.qkv = LoRALinear(blk.attn.qkv)
    blk.attn.proj = LoRALinear(blk.attn.proj)
for p in model.parameters():  # freeze everything, then switch the LoRA matrices back on
    p.requires_grad = False
for m in model.modules():
    if isinstance(m, LoRALinear):
        m.A.requires_grad = m.B.requires_grad = True

trainable = [p for p in model.parameters() if p.requires_grad]
print(f"trainable parameters: {sum(p.numel() for p in trainable):,} of {total:,} ({100 * sum(p.numel() for p in trainable) / total:.1f}%)")

final = train(model, caps, steps=500, lr=3e-3, log_every=250, params=trainable)
print(f"\nloss on the new task after LoRA fine-tuning: {final:.3f}")
print(sample_text(model, caps, prompt="\n", n=200))
