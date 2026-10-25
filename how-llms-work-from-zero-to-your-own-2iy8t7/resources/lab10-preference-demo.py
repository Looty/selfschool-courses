"""Lab 10 (chapter 10): preference tuning in miniature. A teaching demo, not a language model.

A "policy" chooses between 4 canned replies to one prompt. People prefer some replies to others.
We nudge the policy toward the preferred replies with the DPO loss from the paper (Rafailov et al. 2023),
while a frozen copy (the "reference") keeps it from drifting too far.

Setup:  uv venv && uv pip install torch
Run:    python lab10-preference-demo.py
"""
import torch
import torch.nn.functional as F

replies = ["I don't know.", "Here is a clear, correct answer.", "Here is a rude answer.", "Here is a long, rambling answer."]
# Human judgements as (preferred, rejected) pairs, by index into `replies`.
pairs = [(1, 0), (1, 2), (1, 3), (3, 2), (0, 2)]

logits = torch.zeros(len(replies), requires_grad=True)  # the policy starts with no opinion
ref_logp = F.log_softmax(logits.detach().clone(), dim=0)  # frozen reference = the starting policy
beta = 0.5  # how strongly to stay near the reference

opt = torch.optim.Adam([logits], lr=0.1)
for step in range(201):
    logp = F.log_softmax(logits, dim=0)
    loss = 0.0
    for win, lose in pairs:
        # DPO: raise the preferred reply's probability relative to the reference, lower the rejected one's.
        margin = beta * ((logp[win] - ref_logp[win]) - (logp[lose] - ref_logp[lose]))
        loss = loss - F.logsigmoid(margin)
    loss = loss / len(pairs)
    opt.zero_grad()
    loss.backward()
    opt.step()
    if step in (0, 50, 200):
        probs = F.softmax(logits, dim=0).detach()
        print(f"\nstep {step}: loss {loss.item():.3f}")
        for r, p in zip(replies, probs):
            print(f"  {p:5.2f}  {r}")
