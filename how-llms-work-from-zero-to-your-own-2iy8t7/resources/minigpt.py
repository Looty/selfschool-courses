"""A tiny character-level GPT in PyTorch (about 120 lines). Used by labs 8, 9, 11 and 13.

It follows the design of "Attention Is All You Need" (decoder only, like GPT) at a toy scale:
token embeddings + position embeddings -> N blocks of (causal self-attention, then a small MLP,
each with a residual connection and layer norm) -> a final layer that scores every character.

Setup:  uv venv && uv pip install torch numpy
Needs:  input.txt in the current folder (python lab-corpus.py)
"""
import math
import time
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class Config:
    block_size: int = 64   # context window: how many characters the model sees at once
    n_layer: int = 2       # number of Transformer blocks
    n_head: int = 4        # attention heads per block
    n_embd: int = 64       # size of each character's vector
    dropout: float = 0.0


class SelfAttention(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.n_head = c.n_head
        self.qkv = nn.Linear(c.n_embd, 3 * c.n_embd)  # queries, keys and values in one matrix
        self.proj = nn.Linear(c.n_embd, c.n_embd)
        self.register_buffer("mask", torch.tril(torch.ones(c.block_size, c.block_size)).view(1, 1, c.block_size, c.block_size))

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q, k, v = (t.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) for t in (q, k, v))
        att = (q @ k.transpose(-2, -1)) / math.sqrt(k.size(-1))
        att = att.masked_fill(self.mask[:, :, :T, :T] == 0, float("-inf"))  # no peeking at later characters
        y = F.softmax(att, dim=-1) @ v
        return self.proj(y.transpose(1, 2).contiguous().view(B, T, C))


class Block(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(c.n_embd), nn.LayerNorm(c.n_embd)
        self.attn = SelfAttention(c)
        self.mlp = nn.Sequential(nn.Linear(c.n_embd, 4 * c.n_embd), nn.GELU(), nn.Linear(4 * c.n_embd, c.n_embd))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))  # residual connection: add the input back
        return x + self.mlp(self.ln2(x))


class MiniGPT(nn.Module):
    def __init__(self, vocab_size: int, c: Config):
        super().__init__()
        self.c = c
        self.tok = nn.Embedding(vocab_size, c.n_embd)
        self.pos = nn.Embedding(c.block_size, c.n_embd)
        self.blocks = nn.Sequential(*[Block(c) for _ in range(c.n_layer)])
        self.ln_f = nn.LayerNorm(c.n_embd)
        self.head = nn.Linear(c.n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))
        logits = self.head(self.ln_f(self.blocks(x)))
        loss = None if targets is None else F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, n_new: int, temperature: float = 1.0):
        for _ in range(n_new):
            logits, _ = self(idx[:, -self.c.block_size:])
            probs = F.softmax(logits[:, -1, :] / temperature, dim=-1)
            idx = torch.cat([idx, torch.multinomial(probs, 1)], dim=1)
        return idx


class Data:
    """Character-level data: the 'tokenizer' is simply one id per distinct character."""

    def __init__(self, path: str = "input.txt"):
        text = open(path, encoding="utf-8").read()
        self.chars = sorted(set(text))
        self.stoi = {ch: i for i, ch in enumerate(self.chars)}
        data = torch.tensor([self.stoi[ch] for ch in text], dtype=torch.long)
        n = int(0.9 * len(data))
        self.train, self.valid = data[:n], data[n:]

    def encode(self, s: str):
        return [self.stoi[ch] for ch in s]

    def decode(self, ids) -> str:
        return "".join(self.chars[i] for i in ids)

    def batch(self, split: str, size: int, block: int):
        d = self.train if split == "train" else self.valid
        ix = torch.randint(len(d) - block - 1, (size,))
        x = torch.stack([d[i : i + block] for i in ix])
        y = torch.stack([d[i + 1 : i + block + 1] for i in ix])  # the target is the input shifted by one
        return x, y


@torch.no_grad()
def eval_loss(model, data: Data, batch_size: int = 32, iters: int = 20) -> float:
    model.eval()
    out = {}
    for split in ("train", "valid"):
        losses = [model(*data.batch(split, batch_size, model.c.block_size))[1].item() for _ in range(iters)]
        out[split] = sum(losses) / iters
    model.train()
    return out["valid"]


def train(model, data: Data, steps: int, lr: float = 3e-3, batch_size: int = 32, log_every: int = 100, params=None):
    opt = torch.optim.AdamW(params if params is not None else model.parameters(), lr=lr)
    t0 = time.time()
    for step in range(steps + 1):
        if step % log_every == 0:
            print(f"step {step:5d}  valid loss {eval_loss(model, data):.3f}  ({time.time() - t0:.0f}s)")
        if step == steps:
            break
        _, loss = model(*data.batch("train", batch_size, model.c.block_size))
        opt.zero_grad()
        loss.backward()
        opt.step()
    return eval_loss(model, data)


def n_params(model) -> int:
    return sum(p.numel() for p in model.parameters())


def sample_text(model, data: Data, prompt: str = "\n", n: int = 300, temperature: float = 0.8) -> str:
    idx = torch.tensor([data.encode(prompt)], dtype=torch.long)
    return data.decode(model.generate(idx, n, temperature)[0].tolist())
