<div align="center">

# 🔬 llm-lab — a local LLM research lab with a method

**Baseline → hypothesis → experiment → evaluation → generalization.**
On a single consumer GPU (AMD RX 9070 XT 16 GB, Windows), no cloud, no API keys.

</div>

---

## 1. What this is

A personal lab where I *measure* a local coding agent instead of trusting vibes.
Every claim in this README has a run behind it in `results/`, including the ones
that failed — which is most of them, and that is the point.

**Headline results**

| Phase | What ran | Result |
|---|---|---|
| 0 | Baseline, 50 verifiable tasks | **49/50 (98 %)** — one real failure (`sh-005`) |
| 1 | Hybrid RAG over a real repo (BM25 + dense, bge-m3) | retrieval **10/10** (dense-only: 9/10) |
| 1 | Bridge tasks that require the repo spec | without RAG **≈0-1/7** → with RAG **≈4-5/7** |
| 2 | QLoRA (8 attention layers, 0.068 % of params) | pipeline works, **aggregate did not move** (reported as such) |
| 3 | **GRPO with verifiable reward** (repo tests as the reward) | **2/7** without context vs 1/7 baseline — solved a task nothing else ever did |
| 3b | GRPO with **dense reward** (assert coverage) | training signal in **71 %** of steps vs 33 %; **ct-07 passed for the first time in the lab's history** |

---

## 2. Problem

Local models are easy to *try* and hard to *improve*, because "it feels better" is
not evidence. Without a frozen harness, a baseline and honest reporting, every
tweak looks like progress. The other half of the problem: my own production repo
(contabilia) has a specification a 9B local model simply does not know, so it
hallucinates generic advice instead of using the real one.

## 3. Solution

A four-phase lab with a single rule: **never change the harness mid-comparison.**

1. A measurable baseline with automatically verified tasks (`evals/`).
2. Retrieval over the real repository, measured with hit-rate plus a bridge of
   tasks that can only be solved by reading the actual spec.
3. Real fine-tuning (QLoRA) with ablations, not a copy-pasted tutorial.
4. Reinforcement learning where the **reward is the repository's own tests** — the
   prompt never sees the tests, the reward does.

## 4. Architecture

```
              eval harness (evals/run_eval.py)
              - test_kind: python | bash | sql | answer
              - reward 1.0 if the test passes  ---------------+
                                                              |
  Phase 1  RAG (rag/)                                         |
  docs -> fence-aware chunking -> bge-m3 embeddings -> store   |
                |                                             |
                +--> hybrid retrieval (BM25 + dense, a=0.4) --+
                                                              v
  Phase 2/3  training (fase2/)                       Qwen3.5-9B served by Ollama
  base -> QLoRA (attention-only) -> merge -> GGUF Q4_K_M -> local-qwen-ft
                                     |
                                     +--> GRPO: reward = verify_task (0/1)
                                                or assert-coverage (dense)
```

See `docs/architecture.md` for the full reasoning, including the five iterations it
took to make the RAG honest.

## 5. Features

- **Verifiable eval harness** — 50 tasks across algorithms, debugging, python_core,
  reasoning, SQL and bash, with `python`, `bash`, `sql` and exact-`answer` checks.
- **Fence-aware chunking** — the first index split functions in half; the fix took
  the corpus from 811 to 555 real chunks and retrieval from 9/10 to 10/10.
- **Hybrid retrieval** — BM25 + dense with a weight I can justify (alpha = 0.4),
  because a giant PRD paragraph was drowning the duplicates section.
- **Real QLoRA** — LoRA on the 8 full-attention layers of Qwen3.5-9B-Base
  (0.068 % of parameters), 140 examples, 2 epochs, loss 1.51 -> 0.86, 8.82 GB VRAM.
- **Real GRPO** — TRL + Unsloth, with a binary reward and a dense assert-coverage
  reward, using the SFT adapter as the KL reference so RL-vs-SFT is isolated.
- **Reproducible on Windows + ROCm** — including the four Windows traps and the
  distributed shims that make it work (`fase2/sitecustomize.py`).

## 6. Tech stack

| Layer | Technology |
|---|---|
| Models | Qwen3.5-9B-Base, Qwen3-14B (serving), bge-m3 embeddings |
| Training | Unsloth, TRL (GRPOTrainer), PEFT/LoRA, bitsandbytes 4-bit, PyTorch ROCm |
| Serving / evals | Ollama, llama.cpp (Vulkan), custom Python harness |
| Hardware | AMD RX 9070 XT 16 GB (RDNA4), 32 GB RAM, Windows |
| Language | Python 3.12+ |

## 7. Results

### Phase 0 — baseline `local-qwen:latest` (2026-09-22)

| Category | Solved | % |
|---|---|---|
| algorithms | 10/10 | 100 % |
| debugging | 10/10 | 100 % |
| python_core | 10/10 | 100 % |
| reasoning | 10/10 | 100 % |
| sql | 5/5 | 100 % |
| bash | 4/5 | 80 % |
| **Total** | **49/50** | **98 %** |

This is the **zero point**: every later phase is measured against it.

### Phase 1 — hybrid RAG

- Corpus: a real production repository, chunked with fence awareness.
- Retrieval hit-rate **10/10** (dense-only 9/10); qualitatively, without context the
  9B invents generic accounting theory, with context it cites real Prisma models.
- Bridge (`rag/code_tasks.jsonl`, ct-01..ct-07): **without RAG ~0-1/7, with RAG ~4-5/7**.

### Phase 2 — QLoRA and an honest negative result

Merged to GGUF Q4_K_M and imported into Ollama as `local-qwen-ft`. Bridge eval:
**0/7 without RAG** (baseline 1/7), **4/7 with RAG**. Published as-is: the pipeline
is correct, but an attention-only LoRA trained on 140 examples does not move the
aggregate. Next lever: a bigger dataset, or starting from the instruct model.

### Phase 3 — GRPO with verifiable reward

28 steps (~1.5 h), `g=3`, temp 0.8, lr 2e-5, healthy KL (0.0003-0.0005), 8/28 steps
with reward > 0, VRAM 9.06 GB stable / 15.06 GB peak.

| | baseline | SFT | **RL** | baseline+RAG | SFT+RAG | **RL+RAG** |
|---|---|---|---|---|---|---|
| Bridge total | 1/7 | 0/7 | **2/7** | 4/7 | 4/7 | 4/7 |

The RL run solved `ct-06` (FIFO cash application) — a task neither the baseline nor
the SFT ever passed. Every retrieval was a hit: the bottleneck was reasoning, not
retrieval.

### Phase 3b — dense reward (assert coverage)

A binary reward throws away the signal of the almosts: a solution passing 3 of 5
asserts scored the same as one that produced nothing. Switching to assert-coverage:

| Metric | Binary | Dense |
|---|---|---|
| Steps with signal | ~7/21 (33 %) | **~15/21 (71 %)** |
| Best reward | 0.333 | **0.389** |
| Fine-grained signal (<0.2) | almost none | abundant |

And on the bridge, with RAG: **5/7 in a single run**, with `ct-07` passing **for the
first time in the lab's history** (it fails by exactly one key, `unidentified` vs
`conciliated`, with the other 8 exact). Full tables in
`results/fase3_grpo_vs_fase2.md` and `results/fase3b_dense_vs_binary.md`.

## 8. Demo

There is no hosted demo on purpose — the whole point is that this runs on local
hardware. To reproduce the baseline:

```bash
cd evals
python run_eval.py --model local-qwen:latest --tasks tasks.jsonl
```

To run the bridge with the reward that drives the RL:

```bash
cd rag   # run_code_rag.py expects this cwd
python run_code_rag.py --model local-qwen-rl2:latest
```

## 9. Installation

```bash
# 1) Model serving
ollama pull qwen3.5:9b            # or import your own GGUF
ollama pull bge-m3                # embeddings for the RAG

# 2) Evaluation harness
cd evals
python -m pip install httpx
python run_eval.py --model local-qwen:latest --tasks tasks.jsonl --limit 5

# 3) Build the RAG index
cd ../rag
python index_rag.py               # builds data/chunks.json + data/vectors.npy
python run_rag_eval.py

# 4) Training (Windows + ROCm; see fase2/sitecustomize.py for the shims)
cd ../fase2
python -m venv .venv
.venv/Scripts/python -m pip install unsloth trl peft
.venv/Scripts/python train_grpo.py --dry-run    # wires model + dataset + reward
```

## 10. Roadmap

- [ ] Consolidate the dense-reward run (Phase 3c): ct-02/03/04/07 are "almost" —
      they need more steps, not a new method.
- [ ] Lower eval temperature (0.6 -> 0.3) or report median/max over N runs, to remove
      the sampling variance that makes single runs noisy.
- [ ] Publish the eval dependencies in a `rag/requirements.txt` (one bridge task died
      from a missing `holidays` package, a legitimate dependency of the domain).
- [ ] Distill the 4-bit/ROCm workarounds into one documented setup script.
- [ ] Extend the harness beyond a single repo: the pattern should transfer.

## 11. Lessons learned

1. **A harness you never change mid-comparison is worth more than a clever prompt.**
   Five iterations of the RAG were only interpretable because the tasks stayed frozen.
2. **Chunking is where RAG fails silently.** Splitting a function in half does not
   crash anything — it just quietly removes the answer. 811 -> 555 chunks fixed it.
3. **Publish negative results.** "The QLoRA did not move the aggregate" is more
   useful than a fake improvement, and it is what pointed at the RL phase.
4. **A binary reward wastes most of the signal.** The dense assert-coverage reward
   went from 33 % to 71 % of steps with usable signal — same tests, new arithmetic.
5. **Keep the tests out of the prompt.** The model only ever sees the task; the
   reward sees the verification. Otherwise you measure memorization, not ability.
6. **Windows + ROCm + RDNA4** hid four specific traps (documented in
   `docs/architecture.md`) plus missing distributed shims. It runs — it is just not
   the path of least resistance.

## 12. Repository layout

```
evals/    harness: tasks.jsonl (50 tasks), run_eval.py, make_tasks.py
rag/      chunking, hybrid retrieval, bridge tasks (ct-01..ct-07), code RAG runner
fase2/    QLoRA + GRPO training scripts, reward scoring, merges, GGUF export
docs/     architecture.md - full reasoning and the Windows/ROCm traps
results/  every eval run: raw jsonl + markdown summaries (including failures)
README.es.md   the original Spanish version of this document
```

---

*Spanish version: `README.es.md`. Everything runs offline; no data leaves the machine.*

---

## 13. License

MIT © 2026 Alejo Fernandez Di Piramo — see [LICENSE](LICENSE).
