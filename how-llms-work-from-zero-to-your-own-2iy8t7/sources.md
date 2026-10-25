# Sources

Numbers are stable: lessons and questions cite them as `[n]`. Never renumber; append new sources at the end.
Only list sources that were actually read during research. Never invent a URL.

1. [Attention Is All You Need](https://arxiv.org/abs/1706.03762) · Vaswani et al., arXiv · accessed 2026-10-25 · reliability: high
   - Notes: full text read (arXiv PDF, extracted locally). N = 6 layers, d_model = 512, h = 8 heads with d_k = d_v = 64; post-layer-norm `LayerNorm(x + Sublayer(x))`; sinusoidal positional encodings (learned ones gave nearly identical results); Table 1 complexity; Adam with warmup 4000; 8 P100 GPUs, 12 hours base / 3.5 days big; 28.4 BLEU EN-DE, 41.8 BLEU EN-FR; submitted 12 June 2017.
2. [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361) · Kaplan et al., arXiv · accessed 2026-10-25 · reliability: high
   - Notes: abstract only; loss follows power laws in model size, data and compute; January 2020.
3. [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) · Brown et al., arXiv · accessed 2026-10-25 · reliability: high
   - Notes: full text partly read (Section 1 to 2.1 and the contamination discussion). 8 model sizes from 125M to 175B; GPT-3 has 96 layers, d_model 12288, 96 heads; all trained on 300 billion tokens; same architecture as GPT-2 with alternating dense and locally banded sparse attention; contamination study; May 2020.
4. [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) · Ouyang et al., arXiv · accessed 2026-10-25 · reliability: high
   - Notes: full text partly read (Sections 1 to 3). 40 contractors as labelers; supervised demonstrations, then comparisons for a reward model, then PPO; "alignment tax" and the PPO-ptx fix (mixing in pretraining updates); the 1.3B PPO-ptx model preferred to 175B GPT-3; the language-modelling objective is "misaligned" with following instructions; March 2022.
5. [Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) · Bahdanau, Cho, Bengio, arXiv · accessed 2026-10-25 · reliability: high
   - Notes: full text partly read (ICLR 2015 version). Encoder is a bidirectional RNN (1000 hidden units), the alignment model is a small feed-forward network trained jointly, "soft alignment" lets gradients flow, models trained for about 5 days, beam search at decoding; RNNsearch vs RNNencdec comparison.
6. [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) · Sennrich, Haddow, Birch, arXiv · accessed 2026-10-25 · reliability: high
   - Notes: abstract only; byte pair encoding for subword vocabularies, 2015, ACL 2016.
7. [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) · Mikolov et al., arXiv · accessed 2026-10-25 · reliability: high
   - Notes: abstract only; word vectors learned in under a day from 1.6 billion words; January 2013.
8. [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556) · Hoffmann et al., arXiv · accessed 2026-10-25 · reliability: high
   - Notes: full text partly read. Fitted exponents about 0.5 for parameters and 0.5 for tokens (Kaplan et al.: 0.73 and 0.27); Table 3 gives about 20 tokens per parameter (1B parameters: 20.2B tokens); Chinchilla 70B trained on 1.4 trillion tokens; "inference cost" argument; March 2022.
9. [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) · Devlin et al., arXiv · accessed 2026-10-25 · reliability: high
   - Notes: abstract only; bidirectional pre-training then fine-tuning; October 2018.
10. [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) · Hu et al., arXiv · accessed 2026-10-25 · reliability: high
    - Notes: full text partly read; freezes the weights and trains small low-rank matrices; trainable parameters can be as small as 0.01% of GPT-3 175B's; adapter layers add inference latency; abstract: up to 10,000 times fewer trainable parameters and 3 times less GPU memory; June 2021.
11. [LLaMA: Open and Efficient Foundation Language Models](https://arxiv.org/abs/2302.13971) · Touvron et al., arXiv · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; 7B to 65B models trained on public data, LLaMA-13B beats GPT-3 on most benchmarks; February 2023.
12. [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) · Wei et al., arXiv · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; January 2022.
13. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) · Yao et al., arXiv · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; interleaving reasoning with tool use (a Wikipedia API); October 2022.
14. [Direct Preference Optimization](https://arxiv.org/abs/2305.18290) · Rafailov et al., arXiv · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; a simpler alternative to RLHF's reinforcement-learning step; May 2023.
15. [A Neural Probabilistic Language Model](https://www.jmlr.org/papers/v3/bengio03a.html) · Bengio et al., JMLR 3, 2003 · accessed 2026-10-25 · reliability: high
    - Notes: full text partly read; the curse of dimensionality and the proposed fix ("each training sentence informs the model about an exponential number of semantically neighbouring sentences"); modified Kneser-Ney n-grams as baseline; the AP News run was 5 epochs over 3 weeks on 40 CPUs.
16. [Computing Machinery and Intelligence](https://academic.oup.com/mind/article/LIX/236/433/986238) · A. M. Turing, Mind 1950 · accessed 2026-10-25 · reliability: high
    - Notes: only the opening page was readable; "Can machines think?" and the imitation game.
17. [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) · GitHub README · accessed 2026-10-25 · reliability: medium
    - Notes: marked "very old and deprecated" (November 2025 update) in favour of nanochat; the CPU config (4 layers, 128 embedding) trains in about 3 minutes to loss about 1.88; character-level Shakespeare.
18. [karpathy/nanochat](https://github.com/karpathy/nanochat) · GitHub README · accessed 2026-10-25 · reliability: medium
    - Notes: "simplest experimental harness for training LLMs"; about 2 hours on 8 H100s, about $48; MIT licence.
19. [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html) · Andrej Karpathy · accessed 2026-10-25 · reliability: medium
    - Notes: lecture list (micrograd, makemore bigram and MLP, tokenizer, Let's build GPT); used as a model for the lab sequence, not as a source of facts.
20. [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) · Jay Alammar · accessed 2026-10-25 · reliability: medium
    - Notes: step-by-step description of self-attention (queries, keys, values, scaled dot product, softmax); a teaching blog.
21. [Large language model](https://en.wikipedia.org/wiki/Large_language_model) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: first 100,000 of 287,537 characters read; timeline 2017 to 2025, definitions of tokens, context window, pretraining, instruction tuning, RLHF, reasoning models, tool use, hallucination. A tertiary source: use for orientation, verify claims in the primary papers.
22. [ELIZA](https://en.wikipedia.org/wiki/ELIZA) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: Weizenbaum, MIT, published 1966, keyword and script based, the ELIZA effect.
23. [Dartmouth workshop](https://en.wikipedia.org/wiki/Dartmouth_workshop) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: proposal submitted 2 September 1955, workshop summer 1956, organisers McCarthy, Minsky, Rochester, Shannon; the term "artificial intelligence".
24. [Perceptron](https://en.wikipedia.org/wiki/Perceptron) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: first 100,000 of 126,530 characters read; Rosenblatt 1958; Minsky and Papert 1969 and the XOR limit of single-layer perceptrons.
25. [Backpropagation](https://en.wikipedia.org/wiki/Backpropagation) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: first 100,000 of 190,637 characters read; the 1986 Rumelhart, Hinton and Williams section was NOT read; earlier history and what backpropagation computes.
26. [AI winter](https://en.wikipedia.org/wiki/AI_winter) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: first 100,000 of 118,197 characters read; the two winters, the Lighthill report (1973), a historian disputes the first winter was a true one.
27. [Long short-term memory](https://en.wikipedia.org/wiki/Long_short-term_memory) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: first 100,000 of 149,763 characters read; secondary overview (Hochreiter and Schmidhuber 1997, vanishing gradients, Google 2016 translation). The original paper is now source 39 below.
28. [GPT-2](https://en.wikipedia.org/wiki/GPT-2) · Wikipedia · accessed 2026-10-25 · reliability: medium
    - Notes: announced 14 February 2019, 1.5B parameters, WebText 40 GB, staged release.
29. [openai-community/gpt2 model card](https://huggingface.co/openai-community/gpt2) · Hugging Face · accessed 2026-10-25 · reliability: high
    - Notes: the 124M version, MIT licence, WebText, intended use, bias warning, `pipeline('text-generation', model='gpt2')`.
30. [Text generation (transformers)](https://huggingface.co/docs/transformers/en/llm_tutorial) · Hugging Face docs · accessed 2026-10-25 · reliability: high
    - Notes: `generate()`, `max_new_tokens` (default is only 20 tokens), greedy versus sampling, temperature, chat templates.
31. [A Mathematical Theory of Communication](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf) · C. E. Shannon, Bell System Technical Journal 27 (1948), reprinted with corrections · accessed 2026-10-25 · reliability: high
    - Notes: full text read (PDF extracted locally). Section 3 "The series of approximations to English" gives the zero-, first-, second- and third-order letter samples and the first- and second-order word samples over a 27-symbol alphabet; how they were generated (random-number book, then opening a book at random); the redundancy of English is roughly 50%.
32. [Linear regression: Gradient descent](https://developers.google.com/machine-learning/crash-course/linear-regression/gradient-descent) · Google Machine Learning Crash Course · accessed 2026-10-25 · reliability: high
    - Notes: loss surface, gradient of MSE, update rule, convergence; the page calls the step size a "small amount" and uses 0.01 as an arbitrary example.
33. [Neural networks: Nodes and hidden layers](https://developers.google.com/machine-learning/crash-course/neural-networks/nodes-hidden-layers) · Google Machine Learning Crash Course · accessed 2026-10-25 · reliability: high
    - Notes: neurons as weighted sums plus bias, hidden layers, parameters (21 in the 3-4-1 example), why a nonlinearity is needed. Activation functions themselves are on the next page, which was not read.
34. [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary) · Google for Developers · accessed 2026-10-25 · reliability: high
    - Notes: first 100,000 of 445,129 characters read; cross-entropy ("a generalization of log loss to multi-class classification"), bigram ("an N-gram in which N=2"). Softmax, logits, temperature and perplexity were not in the part read.
35. [Overfitting](https://developers.google.com/machine-learning/crash-course/overfitting/overfitting) · Google Machine Learning Crash Course · accessed 2026-10-25 · reliability: high
    - Notes: overfitting, generalisation, training versus validation loss curves, two causes.
36. [Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110) · Liang et al., arXiv / TMLR 2023 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; 42 scenarios, 7 metrics (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency), 30 models; November 2022.
37. [TruthfulQA: Measuring How Models Mimic Human Falsehoods](https://arxiv.org/abs/2109.07958) · Lin, Hilton, Evans, arXiv / ACL 2022 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; 817 questions, best model truthful on 58% vs 94% for humans, larger models generally less truthful.
38. [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) · Lewis et al., arXiv / NeurIPS 2020 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; parametric plus non-parametric memory; May 2020.
39. [Long Short-Term Memory](https://deeplearning.cs.cmu.edu/F23/document/readings/LSTM.pdf) · Hochreiter and Schmidhuber, Neural Computation 9 (1997) · accessed 2026-10-25 · reliability: high
    - Notes: original paper, abstract and introduction read from the extracted PDF. Error signals flowing backward in time "blow up or vanish"; constant error carousels; multiplicative gate units; bridges time lags of more than 1000 steps; O(1) computation per time step and weight.
40. [ELIZA: a computer program for the study of natural language communication between man and machine](https://web.stanford.edu/class/linguist238/p36-weizenabaum.pdf) · J. Weizenbaum, Communications of the ACM, January 1966 · accessed 2026-10-25 · reliability: high
    - Notes: scanned paper, OCR text partly noisy. Keywords and transformation rules, the Rogerian scripts, and Weizenbaum's own explanation that the psychiatric interview was chosen because one participant can pose as knowing almost nothing of the real world.
41. [Improving Language Understanding by Generative Pre-Training](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) · Radford, Narasimhan, Salimans, Sutskever, OpenAI, 2018 · accessed 2026-10-25 · reliability: high
    - Notes: GPT-1, full text read. Generative pre-training then discriminative fine-tuning; 12-layer decoder-only Transformer, 768-dimensional states, 12 heads, 3072 inner feed-forward size; BooksCorpus (over 7,000 unpublished books); sequences of 512 tokens; BPE with 40,000 merges; learned position embeddings; GELU; best on 9 of 12 tasks.
42. [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) · Radford et al., OpenAI, 2019 · accessed 2026-10-25 · reliability: high
    - Notes: GPT-2, full text read. Four sizes 117M, 345M, 762M, 1542M parameters (12, 24, 36, 48 layers); layer norm moved to the input of each sub-block; vocabulary 50,257; context 1024; byte-level BPE with a base vocabulary of 256; WebText; zero-shot results; the largest model "still underfits WebText".
43. [Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) · Sutskever, Vinyals, Le, arXiv / NeurIPS 2014 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; LSTM encoder and decoder, 34.8 BLEU vs 33.3 for a phrase-based baseline on WMT'14 EN-FR; reversing the source sentence helped.
44. [Layer Normalization](https://arxiv.org/abs/1607.06450) · Ba, Kiros, Hinton, arXiv, July 2016 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; statistics from all inputs of one layer for one training case; independent of batch size; same computation at training and test time.
45. [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385) · He et al., arXiv, December 2015 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; layers learn residual functions relative to their inputs; networks up to 152 layers; easier to optimise.
46. [Adam: A Method for Stochastic Optimization](https://arxiv.org/abs/1412.6980) · Kingma and Ba, arXiv / ICLR 2015 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; first-order method using adaptive estimates of lower-order moments of the gradients; low memory; little tuning.
47. [Distributed Representations of Words and Phrases and their Compositionality](https://arxiv.org/abs/1310.4546) · Mikolov et al., arXiv / NeurIPS 2013 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; skip-gram, subsampling of frequent words, negative sampling, phrases.
48. [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) · Schulman et al., arXiv, July 2017 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; a reinforcement-learning method that alternates collecting data and optimising a surrogate objective over several epochs of minibatch updates; simpler than trust-region methods.
49. [Deep reinforcement learning from human preferences](https://arxiv.org/abs/1706.03741) · Christiano et al., arXiv, June 2017 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; goals defined by non-expert comparisons of trajectory segments; feedback on less than 1% of interactions; about an hour of human time for novel behaviours.
50. [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. (Anthropic), arXiv, December 2022 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; critique-and-revise supervised phase; an AI judges which of two responses is better to train a preference model (RLAIF); human oversight only through a short list of written principles.
51. [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774) · OpenAI, arXiv, March 2023 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; accepts image and text inputs; exam performance; "less capable than humans in many real-world scenarios"; models trained with at most 1/1,000th of GPT-4's compute were used to forecast aspects of its performance; the abstract gives no parameter count, architecture, data or compute.
52. [Llama 2: Open Foundation and Fine-Tuned Chat Models](https://arxiv.org/abs/2307.09288) · Touvron et al., arXiv, July 2023 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; 7B to 70B parameters; Llama 2-Chat optimised for dialogue; human ratings of helpfulness and safety.
53. [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI, arXiv January 2025, Nature vol. 645 (2025) · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; reasoning abilities incentivised through pure reinforcement learning without human-labelled reasoning trajectories; self-reflection and verification emerge; reasoning patterns transferred to smaller models.
54. [Emergent Abilities of Large Language Models](https://arxiv.org/abs/2206.07682) · Wei et al., TMLR 2022 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; an ability is emergent if it is not present in smaller models but is present in larger models.
55. [Are Emergent Abilities of Large Language Models a Mirage?](https://arxiv.org/abs/2304.15004) · Schaeffer, Miranda, Koyejo, arXiv, April 2023 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; apparent emergence can come from nonlinear or discontinuous metrics; linear or continuous metrics show smooth improvement.
56. [Measuring Massive Multitask Language Understanding](https://arxiv.org/abs/2009.03300) · Hendrycks et al., ICLR 2021 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; 57 subjects; largest GPT-3 about 20 points above random chance; uneven across subjects; models often do not know when they are wrong.
57. [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) · Schick et al., arXiv, February 2023 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; self-supervised learning of which APIs to call, when and with what arguments; calculator, question answering, search, translation, calendar.
58. [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) · Holtzman et al., ICLR 2020 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; likelihood as a decoding objective gives bland and repetitive text; nucleus sampling.
59. [Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer](https://arxiv.org/abs/1701.06538) · Shazeer et al., arXiv, January 2017 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; a gating network selects a sparse subset of thousands of expert sub-networks per example; up to 137 billion parameters; over 1000x capacity with minor losses in efficiency.
60. [SentencePiece](https://arxiv.org/abs/1808.06226) · Kudo and Richardson, arXiv / EMNLP 2018 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; trains subword models directly from raw sentences; language independent; open source.
61. [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864) · Su et al., arXiv, April 2021 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; encodes absolute position with a rotation matrix and builds relative position dependence into self-attention.
62. [FlashAttention](https://arxiv.org/abs/2205.14135) · Dao et al., arXiv, May 2022 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; exact attention, IO-aware, tiling to reduce memory reads and writes; 3x speedup on GPT-2 at 1K tokens.
63. [Survey of Hallucination in Natural Language Generation](https://arxiv.org/abs/2202.03629) · Ji et al., ACM Computing Surveys 2022 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; generation "is prone to hallucinate unintended text"; metrics, mitigation, task-specific progress and large language models.
64. [On the Opportunities and Risks of Foundation Models](https://arxiv.org/abs/2108.07258) · Bommasani et al., arXiv, August 2021 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; foundation models are trained on broad data at scale and adaptable to many downstream tasks; emergence and homogenisation.
65. [Finetuned Language Models Are Zero-Shot Learners](https://arxiv.org/abs/2109.01652) · Wei et al. (FLAN), arXiv, September 2021 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; instruction tuning a 137B model on over 60 tasks beat zero-shot GPT-3 175B on 20 of 25 tasks.
66. [Mistral 7B](https://arxiv.org/abs/2310.06825) · Jiang et al., arXiv, October 2023 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; outperforms Llama 2 13B on all evaluated benchmarks; grouped-query and sliding-window attention; Apache 2.0.
67. [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) · Dettmers et al., arXiv, May 2023 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; 4-bit quantised frozen model with LoRA adapters; a 65B model on a single 48 GB GPU.
68. [Universal Language Model Fine-tuning for Text Classification](https://arxiv.org/abs/1801.06146) · Howard and Ruder, ACL 2018 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; fine-tune a pretrained language model for classification; with 100 labelled examples it matches training from scratch on 100 times more data.
69. [Deep contextualized word representations](https://arxiv.org/abs/1802.05365) · Peters et al. (ELMo), NAACL 2018 · accessed 2026-10-25 · reliability: high
    - Notes: abstract only; word vectors from the internal states of a deep bidirectional language model; they handle polysemy.
70. [The Unreasonable Effectiveness of Recurrent Neural Networks](https://karpathy.github.io/2015/05/21/rnn-effectiveness/) · Andrej Karpathy, blog, 21 May 2015 · accessed 2026-10-25 · reliability: medium
    - Notes: a character-level model on Shakespeare, Wikipedia markup, LaTeX and Linux source; low temperature loops; units that track quotes and brackets. A well-known blog by a practitioner, not a paper.
71. [Perplexity of fixed-length models](https://huggingface.co/docs/transformers/perplexity) · Hugging Face documentation · accessed 2026-10-25 · reliability: high
    - Notes: perplexity is the exponentiated average negative log-likelihood and equals the exponentiated cross-entropy; tokenization affects it; sliding-window evaluation for GPT-2 (1024-token context) gave 19.44 without overlap and 16.44 with stride 512.
72. [Large language models (Machine Learning Crash Course)](https://developers.google.com/machine-learning/crash-course/llm) · Google for Developers · accessed 2026-10-25 · reliability: high
    - Notes: introductory page only; definitions of language model, token, N-gram, context, recurrent neural network and the vanishing gradient problem.
73. [Byte-Pair Encoding tokenization](https://huggingface.co/learn/llm-course/chapter6/5) · Hugging Face LLM course, chapter 6 · accessed 2026-10-25 · reliability: high
    - Notes: training and tokenization with BPE, a worked example (hug, pug, pun, bun, hugs: merges ug, un, hug), the unknown-token issue and byte-level BPE.
74. [Cache strategies (KV cache)](https://huggingface.co/docs/transformers/en/kv_cache) · Hugging Face documentation · accessed 2026-10-25 · reliability: high
    - Notes: autoregressive models recompute key and value vectors every step; a KV cache stores them; dynamic, static, offloaded and quantised caches; the cache can occupy a significant share of memory for long contexts.
75. [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) · OWASP GenAI Security Project · accessed 2026-10-25 · reliability: high
    - Notes: the ten risks LLM01 to LLM10 with a one-line description each.
