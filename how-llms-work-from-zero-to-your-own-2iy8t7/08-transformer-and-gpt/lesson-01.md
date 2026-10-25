---
id: l34
title: "The Transformer block"
quiz: quiz-01.yaml
resources: []
sources: [1, 33, 3, 41, 42, 44, 45]
---
After this lesson you can name the parts of a Transformer block and say what each one is for.

## The 2017 result

"Attention Is All You Need" proposed a network architecture, the Transformer, "based solely on attention mechanisms, dispensing with recurrence and convolutions entirely". The authors reported that it was more parallelisable and needed significantly less training time than earlier sequence models, and it reached 28.4 BLEU on WMT 2014 English-to-German translation (over 2 BLEU better than the previous best, including ensembles) and a single-model 41.8 BLEU on English-to-French after 3.5 days on eight GPUs. [1] The same design, with changes, now sits under nearly every LLM.

## One block, four parts

A model is a stack of identical **blocks**. The original Transformer's encoder was a stack of N = 6 identical layers, each with two sub-layers: multi-head self-attention, then "a simple, position-wise fully connected feed-forward network". All sub-layers and the embeddings produce outputs of size d_model = 512. [1] The block has four ingredients.

1. **Layer normalisation** rescales each token's vector so its numbers stay in a sensible range. Layer normalisation (Ba, Kiros and Hinton, 2016) computes its statistics from all the summed inputs of a layer for a single training case, so it does not depend on the batch size and performs "exactly the same computation at training and test times". [44]
2. **Self-attention** (chapter 7): each token mixes in information from other tokens.
3. **A residual connection**: the sub-layer's result is *added* to its input rather than replacing it, so the layer only has to learn a correction. The idea comes from deep residual learning for images (He et al., 2015): layers learn residual functions relative to their inputs, which the authors found easier to optimise and which allowed networks up to 152 layers. [45]
4. **A feed-forward network** (also called the MLP): a small two-layer neural network, applied to each token separately, with a non-linear activation between the layers (lesson 18). [33] Attention moves information *between* tokens; the feed-forward layer transforms each token's information *in place*. In the original, the inner layer has 2048 units for d_model = 512; GPT-1 used 3072 for 768; in the lab's mini-GPT it is four times the token vector. [1][41]

## Where the normalisation goes: post-LN and pre-LN

The 2017 paper wrote each sub-layer as `LayerNorm(x + Sublayer(x))`: add the sub-layer's output to its input *then* normalise ("post-LN"). [1] GPT-2 moved it: "Layer normalization was moved to the input of each sub-block, similar to a pre-activation residual network, and an additional layer normalization was added after the final self-attention block." [42] This "pre-LN" arrangement is what the lab's code uses:

```python
x = x + self.attn(self.ln1(x))   # normalise, attend, add back
x = x + self.mlp(self.ln2(x))    # normalise, transform, add back
```

Both exist in the literature; GPT-2 and GPT-3 (which says it uses "pre-normalization") follow the second. [42][3] GPT-2 also scales the weights of residual layers at initialisation by 1/√N, where N is the number of residual layers, to account for the accumulation along the residual path. [42]

## Why it works well

- **It trains fast.** All tokens are processed at once (lesson 31). [1]
- **It scales.** Blocks are identical, so making a model bigger means more blocks, wider vectors, or both (chapter 9).
- **Everything is differentiable.** Gradient descent can train all the parts together.

:::key-takeaways
- The Transformer dropped recurrence and convolution and relies on attention alone; it trains faster because of parallelism. [1]
- A block = normalisation, self-attention with a residual connection, then a feed-forward network with a residual connection. [1][44][45]
- The 2017 paper normalised after the residual add (post-LN); GPT-2 and GPT-3 normalise at the input of each sub-block (pre-LN). [1][42][3]
- Attention mixes information between tokens; the feed-forward layer processes each token on its own. [33]
:::

:::glossary
- **Transformer**: the neural network design built on attention that underlies modern LLMs. [1]
- **Block**: one repeated unit: attention plus a feed-forward network.
- **Layer normalisation**: rescaling each token's vector to keep numbers in a stable range.
- **Residual connection**: adding a layer's input to its output, so the layer learns only a correction.
- **Feed-forward network (MLP)**: a small neural network applied to each token separately.
- **GELU**: a smooth non-linear activation function used in the lab's mini-GPT.
- **BLEU**: a translation-quality score; higher is better.
:::
