---
id: l64
title: "Making big models cheap to run: KV cache, FlashAttention, MoE"
quiz: quiz-07.yaml
resources: []
sources: [74, 62, 59, 66, 67, 1]
---
After this lesson you can explain four reasons running a big model is expensive, and the standard answer to each.

## 1. Re-reading the whole text every step: the KV cache

Lesson 37's loop runs the model once per new token. The naive way recomputes everything about the earlier tokens each time. The Hugging Face documentation explains why that is wasteful: for autoregressive models, the key and value vectors used to compute attention scores are calculated every time, and "each prediction depends on the previous tokens, which means the model performs the same computations each time". A **KV cache** stores those key-value vectors so they can be reused instead of recomputed. [74]

The price is memory. The documentation says the cache can occupy a significant portion of memory and become a bottleneck for long-context generation, and lists variants that trade speed for memory: a dynamic cache that grows as generation proceeds, a static cache with a fixed pre-allocated size (which helps compilation but wastes attention work on masked slots), an offloaded cache that keeps only the current layer's cache on the GPU, and a quantised cache that stores the values at lower precision, with a warning that quantising can hurt latency when contexts are short. [74] Models with sliding-window attention keep a cache that stops growing at the window size. [74]

## 2. The quadratic cost of attention: FlashAttention

Lesson 31's table showed attention's work growing with n² (the Transformer paper's Table 1: O(n²·d) per layer). [1] FlashAttention (Dao et al., 2022) targets the real bottleneck on GPUs: moving data between the large but slow high-bandwidth memory and the small but fast on-chip memory. It computes **exact** attention but uses tiling to reduce the number of reads and writes between those memories, which the authors prove requires fewer memory accesses than standard attention. Reported results: about a 3x speedup on GPT-2 at sequence length 1,000, 15% end-to-end on BERT-large, and better quality from longer context (0.7 lower perplexity on GPT-2). [62] The idea transfers: on modern hardware, how data moves can matter more than how many arithmetic operations there are.

## 3. Using only part of the model: mixture of experts

A dense model uses all its parameters for every token. The sparsely-gated mixture-of-experts layer (Shazeer et al., 2017) replaces one big feed-forward layer with up to thousands of smaller "expert" sub-networks and a gating network that picks a sparse few for each example. The authors report more than 1000x improvements in model capacity with only minor losses in computational efficiency, with up to 137 billion parameters, and better results than the previous state of the art on language modelling and translation at lower computational cost. [59] The trade is memory (all experts must be stored) for compute (few are used per token).

## 4. Making the numbers smaller: quantisation

Storing each weight in 4 bits instead of 16 cuts memory about fourfold. QLoRA showed that you can even fine-tune through a 4-bit quantised, frozen model: a 65-billion-parameter model on a single 48 GB GPU. [67]

## Architecture tweaks in open models

Mistral 7B (2023) combines two of these ideas in the architecture: grouped-query attention (several query heads share one set of keys and values, which shrinks the KV cache and speeds up inference) and sliding-window attention (each token attends only to a window of recent tokens, handling long sequences at lower cost). Its authors report it outperforms the larger Llama 2 13B on all evaluated benchmarks. [66]

:::low-confidence
Only the abstracts of the FlashAttention, mixture-of-experts, QLoRA and Mistral papers were read, and the Hugging Face cache page in full. The one-line explanation of grouped-query attention above is a standard description rather than a quotation from the Mistral abstract. [62][59][67][66][74]
:::

:::key-takeaways
- The KV cache stores keys and values from earlier tokens so they are not recomputed; it saves compute but costs memory. [74]
- FlashAttention computes exact attention with fewer memory reads and writes. [62]
- Mixture of experts activates only a few experts per token. [59]
- Quantisation (QLoRA) and attention variants (grouped-query, sliding window) shrink memory further. [67][66]
:::

:::glossary
- **KV cache**: stored key and value vectors from earlier tokens, reused at each new step. [74]
- **Memory bandwidth**: how fast data moves between memory and the chip; often the real limit.
- **HBM / SRAM**: a GPU's large, slow main memory and its small, fast on-chip memory.
- **Tiling**: processing data in small blocks that fit in fast memory.
- **Mixture of experts (MoE)**: a layer with many expert sub-networks of which a gating network picks a few per token. [59]
- **Sparse**: using only a small part at a time.
- **Quantisation**: storing numbers with fewer bits.
- **Grouped-query attention**: several query heads sharing one set of keys and values.
- **Sliding-window attention**: attending only to the most recent tokens.
- **Latency vs throughput**: time for one answer vs answers per second.
:::
