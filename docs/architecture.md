# Alejo AI Lab — Arquitectura

## 1. Hardware real y sus límites

| Componente | Spec | Implicación para LLM |
|---|---|---|
| GPU | RX 9070 XT — RDNA4 (gfx1201), **16 GB VRAM** | Tope duro: modelo + KV cache en 16 GB |
| RAM | 32 GB DDR5 | Offload parcial de capas posible (lento); entrenamiento usa memoria compartida en Windows |
| CPU | X3D AM5 (8–16 cores) | Importa poco para LLM; pesa la RAM, no el cache 3D |
| SO | Windows | ROCm oficial solo en Linux → en Windows, **Vulkan/llama.cpp** para inference; **Unsloth (WSL/Win)** para entrenamiento |

**Regla de oro del lab:** un solo modelo cargado a la vez en la GPU (los agentes
custom ya lo exigen). 9B Q4 ≈ 6.6 GB → sobra VRAM para contexto largo. 20B MXFP4
≈ 13 GB → contexto más corto. >20B densos (ej. Gemma 26B) → no entran: descartados.

## 2. Los 4 componentes (no confundir nunca)

```
MODELO    los pesos (conocimiento + patrones aprendidos)
AGENTE    el harness: tools, permisos, loop plan→ejecutar→verificar
MEMORIA   historial, sesiones, notas persistentes, RAG
ENTRENAM. modificación de pesos (LoRA/QLoRA/RL) — SÓLO con evals de por medio
```

Mejorar el agente NO es (solo) entrenar: es contexto → tools → memoria → evals
→ y recién después, pesos.

## 3. Stack elegido (2026)

### Inference (hoy)
- **Ollama 127.0.0.1:11434** (endpoint OpenAI-compatible) sirviendo:
  - `local-qwen:latest` — Qwen3.5-9B Q4_K_M, params afinados para agente
    (temp 0.6, presence 0, 64K ctx, 8K output).
  - `local-gpt-oss:latest` — GPT-OSS 20.9B MXFP4 (temp 0.2, 64K ctx).
- **OpenCode** como harness de agente, con `opencode/big-pickle` de default
  (planificación) y agentes custom apuntando a los modelos locales (ejecución).

### Entrenamiento (fase 2+)
- **Unsloth** — único stack con soporte oficial "full" para RDNA4
  (Windows/WSL/Linux). QLoRA de 9B viable en 16 GB (base 4-bit ≈ 6 GB).
- **Ambiente (verificado 2026-09-22):**
  - ROCm 7.2 soporta **oficialmente** RX 9070 XT (gfx1201): sin parches ni
    vars de entorno raras. También libprcdxg en WSL2.
  - Unsloth es **"full support" para RDNA 4 (gfx1200/gfx1201)** en Windows,
    WSL y Linux; QLoRA bitsandbytes para Radeon ok; instalación automática del
    wheel ROCm correcto.
  - ⚠️ **Python < 3.14** (3.11–3.13): nuestro python de sistema es 3.14 →
    crear env dedicado (uv: `uv venv --python 3.12` o conda).
  - Vías: Unsloth Studio (Desktop app/WebUI, auto) o Unsloth Core (pip,
    scriptable, reproducible — alineado con el método del lab).
  - Fallback: RadeonForge (template QLoRA RDNA4 Windows/WSL2 con smoke test).
  - **Ejecutado 2026-09-22:** `fase2/.venv` (Python 3.12.14 vía uv) con
    `unsloth[amd]` 2026.9.10 + trl (log: `results/fase2_install.log`).
  - **Wheel ROCm en Windows:** `unsloth[amd]` NO bundlea torch (deja el CPU).
    El índice correcto es el de AMD para Windows por arquitectura
    (`repo.amd.com/rocm/whl/gfx120X-all` para gfx1201/gfx1200); pin del
    instalador oficial de Unsloth: `torch>=2.11.0,<2.12.0` +
    `torchvision>=0.26.0,<0.27.0` + `torchaudio>=2.11.0,<2.12.0`
    (rocm7.13 bundleado). Bitsandbytes ≥0.50.2 (prebuilt ROCm; el bug NaN
    4-bit era ≤0.49.2).
  - **⚠️ GPU dual = trampa:** en Windows torch ve 2 devices: la 9070 XT
    (gfx1201/RDNA4) + la **iGPU Radeon** (gfx103X/RDNA2, RAM compartida).
    `device_map="auto"` reparte el modelo y explota con
    `hipErrorInvalidKernelFile` (kernels gfx1201 en gfx1030). Fix:
    `HIP_VISIBLE_DEVICES=0` + `CUDA_VISIBLE_DEVICES=0`.
  - **Prerequisito C++:** Triton en Windows necesita Visual Studio Build
    Tools 2022 + Windows SDK (instalador oficial los baja por winget); sin
    MSVC falla la compilación JIT de kernels (`stdlib.h not found`).
  - **⚠️ Order de imports:** con `trl` importado ANTES que `unsloth`, el
    lazy-import de transformers 5.5 no resuelve `TrainingArguments` ("Could
    not import module ..."). Unsloth debe importarse primero (sus patches
    arreglan el lazy-loader). Aplica a todo script del lab.
  - **⚠️ Trampas de versión transformers 5.5 / trl en configs:** (a)
    `max_steps=None` crashea el `_validate_args` de Trainer (usar
    `max_steps` solo cuando viene explícito); (b) `report_to=None` NO es
    válido — usar `report_to=[]`; (c) `warmup_ratio` deprecado → usar
    `warmup_steps`.
  - Smoke test en `fase2/smoke_test.py` (GPU única) con Qwen3-1.7B:
    1) GPU gfx1201 detectada, 2) Unsloth parchea, 3) QLoRA 3 steps con loss
    decreciente.
  - **SMOKE APROBADO 2026-09-22 (it.7):** Qwen3-1.7B 4-bit + LoRA r16, 10
    steps, **loss 2.17 → 1.43** (media primer tercio 2.03 → último 1.77),
    **VRAM pico 2.0 GB de 17.1** → QLoRA 9B (~6.5 GB según tabla) cabe con
    margen. Bfloat16 activo; Triton compila con VS Build Tools.
  - **Dataset Fase 2 (`fase2/dataset_sft.jsonl`):** 140 ejemplos = 7 tareas
    del puente (ct-01..ct-07, prompts de `rag/code_tasks.jsonl`) × variantes
    de redacción (5 prefijos × 4 sufijos) con las soluciones golden
    (de `rag/sanity_code_tasks.py`) como respuesta. Creado por
    `fase2/build_dataset.py` (seed 7).
  - **Primer QLoRA real (2026-09-22):** `fase2/train_qwen35.py` —
    Qwen3.5-9B-Base 4-bit, LoRA r16 en solo `q/k/v/o_proj` (8 capas
    full-attention, 0.068% de params), 140 ejemplos, 2 epochs, lr 2e-4,
    bf16, adamw_8bit, output `fase2/out_qwen35_attn/`.
  - **Resultado training (2026-09-22):** loss **1.51 → 0.86** en 36 steps
    (train_loss final 1.14), **VRAM pico 8.82 GB** de 17.1. Adapter en
    `fase2/out_qwen35_attn/` (target_modules grabado como regex
    `(language|text).*(self_attn|attention).*(q_proj|k_proj|v_proj|o_proj)`).
  - **Merge OK (2026-09-22):** `save_pretrained_merged(merged_16bit)` de
    Unsloth (cargando el adapter directo — el loader resuelve el base desde
    `adapter_config.json`; el `model_name=` de `from_pretrained` ya no
    existe en esta API). → `fase2/merged_qwen35_attn/` (18 GB bf16).
  - **⚠️ Trampa numpy (2026-09-22):** los wheels ROCm de AMD dejaron el
    `numpy-2.5.3.dist-info` **vacío** (sin METADATA): `import numpy` anda
    pero `importlib.metadata.version('numpy')` → None → el converter de
    GGUF de Unsloth (que importa transformers en subproceso) crasheaba.
    Fix: `uv pip install --force-reinstall numpy==2.5.3`. Además: procesos
    python zombie del training (spawn de `datasets`) lockean los `.pyd` de
    numpy → "Acceso denegado" → matarlos con `taskkill //PID n //F` antes
    de reinstalar.
  - **GGUF (2026-09-22):** `fase2/to_gguf.py` → `save_pretrained_gguf`
    `q4_k_m` → `fase2/gguf_qwen35_attn/`.
  - **Eval post-fine-tune (2026-09-22):** GGUF importado como
    `local-qwen-ft:latest`, corrido con `run_code_rag.py --model local-qwen-ft:latest`
    sobre ct-01..07.
    - **Sin RAG: 0/7** (baselina 1/7) · **Con RAG: 4/7** (baselina 4/7, pero
      DISTINTA composición).
    - Gana ct-03 (la baselina generaba el resumen cortado a mitad →
      SyntaxError; el SFT con código completo lo arregló).
    - Pierde ct-01 (escribió `'conciled'` en vez de `'conciliated'` — el
      nivel de prolijidad léxica del Base no-chat es menor que el del chat).
    - Persisten fallos de fidelidad profunda: ct-06 (FIFO) y ct-07 (keys).
    - **Veredicto:** el pipeline funciona end-to-end, pero QLoRA attention-only
      con 140 ejemplos NO mueve el agregado (4/7 = 4/7 con RAG). Confirma que
      el LoRA captura formato (generación de código largo, SFT) pero no
      conocimiento profundo del dominio → para eso, más datos y/o RL con
      reward verificable (Fase 3). El dataset de 140 ejemplos quedó corto:
      próxima iteración = mina de bugs de kinetix + partir del instruct.
  - Modelos HF confirmados: `Qwen/Qwen3.5-9B-Base` (pre-trained, 19.33 GB) y
    `Qwen/Qwen3.5-9B` (post-trained, base = -Base). Layout verificado:
    `8 × (3 × (Gated DeltaNet → FFN) → 1 × (Gated Attention → FFN))` → 32
    capas, de las cuales **8 son full-attention** (blanco del LoRA).
- **Mapa de módulos Qwen3.5 verificado (transformers 5.5, 2026-09-22):**
  - Ruta real de capas: `model.model.language_model.layers[0..31]`
    (wrapper `Qwen3_5ForConditionalGeneration` → `Qwen3_5Model` → `Qwen3_5TextModel`).
  - Cada `Qwen3_5DecoderLayer` define `self.self_attn` (full-attention, capas
    3,7,11,15,19,23,27,31 según `config.layer_types` / `full_attention_interval: 4`)
    o `self.linear_attn` (GatedDeltaNet, el resto). `mlp` + RMSNorms en ambas.
  - **Los nombres discriminan solos:** `Qwen3_5Attention` expone
    `q_proj` (out = heads×head_dim×2, gated), `k_proj`, `v_proj`, `o_proj`;
    `Qwen3_5GatedDeltaNet` expone `in_proj_qkv/a/b/z`, `out_proj`, `conv1d`,
    `dt_bias`, `A_log`. → `target_modules=["q_proj","k_proj","v_proj","o_proj"]`
    de Unsloth pega **solo** en las 8 full-attention. Verificado con dry-run:
    `fase2/train_qwen35.py --dry-run` → capas tocadas exactamente
    `[3,7,11,15,19,23,27,31]`, 0 módulos DeltaNet, 3,932,160 params (0.068%).
- Qwen3.5 es **híbrido** (3:1 Gated DeltaNet : Gated Attention):
  - LoRA debe apuntar **solo a las capas `full_attention`** (paper 2026:
    attention-only ≥ full-model con 5–10× menos params; DeltaNet-only destruye
    rendimiento).
  - Después de entrenar: `merge_and_unload()` → convert a GGUF
    (adapter hot-swap en llama.cpp roto para qwen35, llama.cpp#21125).
  - Fine-tune en modo **text-only** (desactivar encoder de visión libera VRAM).
- **RL (fase 3):** GRPO con rewards verificables (pytest / tests del harness
  de evals = la misma infraestructura de esta fase 0).

### RAG / memoria (fase 1)
- Vector store numpy propio + embeddings `bge-m3` vía Ollama (D7) indexando los
  proyectos locales de `D:\...\projects\*`. Retrieval híbrido BM25 + denso (D8).
- Lecciones del puente (tareas de código) sobre la pipeline:
  - el hit-rate *a nivel archivo* (Q&A) no alcanza para código: hacen falta
    el chunk correcto (código, no tabla) y, a veces, 2+ chunks del mismo doc;
  - el chunking debe ser **fence-aware** (bloques de código atómicos): v1
    partía funciones y generaba micro-chunks sin señal → re-index v2
    (811→555 chunks) resuelve la cobertura (7/7);
  - los prompts de eval no deben filtrar la respuesta (fuga = sin RAG pasa);
  - el contrato de los tests debe alinearse a los tipos reales del repo
    (`balance.amount`, `customer.name`), no a versiones simplificadas.

## 4. Fases (roadmap de experimentos)

### Fase 0 — Baseline (AHORA)
- [x] Auditar + limpiar stack (7 modelos → 2, config corregida, agentes depurados)
- [x] Scaffold + harness `evals/` con 50 tareas verificables
- [ ] Correr baseline de `local-qwen:latest` y guardar números por categoría
- [ ] (opcional) Baseline de `local-gpt-oss:latest` para comparar modelos

### Fase 1 — Sistema alrededor del cerebro
- [x] RAG del repositorio: corpus `contabilia` (811 chunks) + bge-m3 + BM25
      híbrido → hit-rate 10/10 (así arrancó en 9/10 denso puro; el PRD gigante
      ahogaba la sección de duplicados y el BM25 lo resolvió)
- [x] Experimento sin/con RAG (v1→v2): 10 preguntas de negocio — hit-rate
      10/10 con hybrid alpha 0.4 (v1: 8/10; q04/q08 recuperados). Sin RAG el
      9B alucina teoría genérica; con RAG cita modelos Prisma y docs reales.
      Ver `results/rag_20260922_191127_*`
- [ ] Puente a Fase 2: evals de CÓDIGO verificables que dependen del corpus
      (`rag/code_tasks.jsonl`, ct-01…ct-07) → son el esqueleto del dataset de
      fine-tuning y del reward de GRPO
      - it.1 (19:18): falsos negativos del harness — prompts con fuga de la
        respuesta (ct-04/05/07), truncamiento a 3000 tokens (fence sin cerrar),
        extracción de código frágil, y retrieval que acierta el archivo pero no
        el chunk (ct-01: trajo la tabla de estados, no el `reconcileStatus`).
        Corregido (prompts sin fuga, max_tokens 6000, extractor robusto,
        respuestas completas guardadas).
      - it.2 (19:27): sin RAG 0/7 (sin fugas ✓) · con RAG 3/7. Diagnóstico de
        las 4 fallas → 3 causas reales, todas del pipeline o del contrato:
        (1) chunking: 07 partía `detectDuplicates` a mitad de función y creaba
            micro-chunks de 3 líneas (chunk 535) sin señal → **re-index
            fence-aware** (811→555 chunks, bloques de código atómicos);
        (2) contrato ambiguo: el repo modela `balance`/`customer` como objetos
            (`.amount`/`.name`) y el test los declaraba número/string → tipos
            alineados al repo;
        (3) el modelo necesitaba 2 chunks de `07` (mapeo + resumen) y el dedupe
            por archivo los descartaba → sin dedupe.
        Con el índice nuevo: cobertura oracle de las 7 tareas = 7/7.
        El Q&A (índice previo, 10/10) queda como experimento de registro; en el
        índice nuevo el único cambio es q07 (docs/03 rank 7 — falso negativo
        del chequeo top-5, el contenido sigue en top-5 vía docs/01 + código).
      - it.3 (19:41): con RAG 4/7 — contratos alineados al repo (`balance` como
        dict `{amount}`, `customer` como `{name}`) destrabaron ct-06/ct-07.
      - it.4 (19:56): con RAG 5/7 — RAG_SYS ahora distingue "técnica estándar
        (implementarla)" de "dato de negocio (no inventar)"; ct-03 lista los
        estados internos de entrada para bajar el chunk de la definición del
        mapeo (rank ≥8 → TOP_K=8, MAX_CONTEXT 12000); ct-05 prohíbe filtros
        por columnas no mencionadas. Fallos restantes: ct-06 = respuesta vacía
        transitoria del endpoint, ct-07 = ruido de chunks (shared-types) que
        llevó al modelo a sobre-aplicar un mapeo de estados al estado ya
        mapeado del resumen.
      - it.5 (20:49): sampling determinista (temp 0.2, seed 7) + retry en
        respuestas vacías.
      - **RESULTADO FINAL del puente** (7 tareas con tests verificables):
        sin RAG ≈0-1/7 · con RAG ≈4-5/7 (varianza por sampling). El gap es
        real y medible: el contexto del producto sube ~4-5 puntos sobre
        tareas que requieren spec del repo. Clases de fallo restantes (targets
        de Fase 2): truncamiento del completado (harness), elecciones sutiles
        de spec (ej. parcial por FIFO vs saldo más cercano, aunque el prompt
        dice "más antigua"), y alucinación de keys bajo ruido de contexto
        (ct-07 inventó `_customer`). Tests ct-01…ct-07 = semilla del dataset
        de fine-tuning y rewards de GRPO (Fase 3).
- [ ] Context engineering (system prompt + AGENTS.md por proyecto)
- [ ] Memoria persistente de sesiones (cruzar con el historial del agente)
- [ ] Re-correr el MISMO baseline de evals de código → ¿el contexto del
      proyecto sube el % de código/debugging?

### Fase 2 — Fine-tuning científico
- Dataset: bugs→diagnóstico→patch→test extraídos de proyectos reales
  (300–3.000 ejemplos de alta calidad)
- QLoRA Unsloth: solo capas de atención, rank 16–64, LR 1e-4–3e-4, 1–3 épocas
- Merge → GGUF → mismo baseline → ablations (base vs +prompt vs +RAG vs +LoRA)

### Fase 3 — RL con reward verificable
- GRPO: el modelo escribe código → corre tests → reward 0/1 → optimización
- Misma infraestructura de evals = recompensa automática

## 5. Decisiones registradas

| # | Decisión | Razón |
|---|---|---|
| D1 | Sacar Gemma-26B y duplicados gpt-oss/qwen | No caben / mismo blob, ruido en selector |
| D2 | Default de OpenCode = `opencode/big-pickle` | Pedido del usuario; cloud para planificar |
| D3 | Agentes de ejecución = modelos locales | Privado, gratis, GPU dedicada |
| D4 | LoRA SOLO en capas full_attention | Evidencia paper híbridos 2026 |
| D5 | Contexto 64K para agentes (no 262K) | Equilibrio rendimiento/VRAM para tool-calling |
| D6 | Evals verificables (código que corre) | Deja la puerta abierta a RL fase 3 |
| D7 | RAG: store numpy propio + embeddings Ollama bge-m3 (no ChromaDB aún) | Evita 200 MB de wheels y riesgo en Python 3.14; migramos a Chroma si hace falta |
| D8 | Retrieval híbrido BM25 + denso, alpha 0.4, stopwords es/en | El denso puro fallaba (PRD dominaba); el léxico recuperó la sección de duplicados → hit-rate 10/10 |

## 6. Estructura de directorios

```
D:\ai-lab\
├── README.md
├── docs\architecture.md      ← este archivo
├── evals\
│   ├── tasks.jsonl           ← 50 tareas verificables
│   ├── run_eval.py           ← runner contra Ollama (OpenAI-compatible)
│   └── README.md
├── results\                  ← baselines y experimentos (gitignored)
└── _backup\                  ← archivos retirados (local-coder.md)
```

## 7. Criterio de terminación de una fase

Una fase termina cuando hay **números** (no opiniones): % de resolución por
categoría, comparables entre corridas, con el mismo harness. Sin baseline, no
hay ciencia — solo vibraciones.