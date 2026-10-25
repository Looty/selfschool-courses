"""Lab 4 (chapter 4): learn a straight line by gradient descent, with nothing but numpy.

Setup:  uv venv && uv pip install numpy
Run:    python lab04-gradient-descent.py            (default learning rate 0.01)
Then:   python lab04-gradient-descent.py 0.1        python lab04-gradient-descent.py 0.3
"""
import sys

import numpy as np

lr = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01  # the "small amount" each step moves

# Made-up data: y = 3x + 2 plus a little noise. The model does not know 3 and 2.
rng = np.random.default_rng(0)
x = rng.uniform(0, 1, 50)
y = 3 * x + 2 + rng.normal(0, 0.1, 50)

w, b = 0.0, 0.0  # start knowing nothing
for step in range(1, 1001):
    pred = w * x + b
    loss = np.mean((pred - y) ** 2)  # mean squared error
    # The gradient: how the loss changes if w or b changes a little (derivatives of the MSE).
    grad_w = np.mean((pred - y) * 2 * x)
    grad_b = np.mean((pred - y) * 2)
    # Step against the slope.
    w -= lr * grad_w
    b -= lr * grad_b
    if step in (1, 10, 100, 1000):
        print(f"step {step:4d}  loss {loss:8.4f}  w {w:6.3f}  b {b:6.3f}")
        if not np.isfinite(loss) or loss > 1e6:
            print("the loss blew up: the learning rate is too big")
            break

print(f"learned: y = {w:.2f} x + {b:.2f}   (the truth was y = 3 x + 2)")
