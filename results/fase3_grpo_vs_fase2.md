# Fase 3 — GRPO sobre el puente (reward verificable) vs Fase 2

Fecha: 2026-09-23 · Modelo RL: `local-qwen-rl:latest` (Q4_K_M, 9.2B params)
Base del RL: `merged_qwen35_attn` (SFT fundido). Adapter LoRA r=16 (attention-only),
entrenado con GRPO 28 steps (~1.5 h), g=3, temp 0.8, lr 2e-5, KL sano (0.0003-0.0005).

## Entrenamiento: señal
- 8/28 steps con reward > 0; mejor step: 8 (0.3333 = 1/3 completions PASS).
- KL estable → aprendizaje sin colapso. VRAM 9.06 GB estable / pico 15.06 GB.

## Resultados del puente (7 tests, temp 0.2 determinístico)

| Test | Baselina sinRAG | FT sinRAG | **RL sinRAG** | Baselina conRAG | FT conRAG | **RL conRAG** |
|---|---|---|---|---|---|---|
| ct-01 states | – | FAIL | FAIL | – | FAIL | **PASS** |
| ct-02 duplicates | – | FAIL | FAIL | – | PASS | FAIL |
| ct-03 summary | – | FAIL | **PASS** | – | PASS | **PASS** |
| ct-04 sql_schema | – | FAIL | FAIL | – | PASS | **PASS** |
| ct-05 sql_duplicates | – | FAIL | FAIL | – | PASS | **PASS** |
| ct-06 cash_application | FAIL | FAIL | **PASS** 🏆 | FAIL | FAIL | FAIL |
| ct-07 export | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Total** | **1/7** | **0/7** | **2/7** | **4/7** | **4/7** | **4/7** |

<small>Baselina = `local-qwen:latest` (sin FT). Valores de baselina por test según resumen Fase 2 (1/7 y 4/7).</small>

## Lectura
1. **El GRPO movió la aguja sin contexto**: 2/7 vs 1/7 baselina y 0/7 FT. Resolvió ct-06
   (cash_application FIFO), uno de los dos puntos que ni baselina ni FT pasaban nunca, y ct-03.
2. **Con RAG empata 4/7**, pero cambió el desglose: ganó ct-01 (nuevo PASS) y perdió ct-02.
   En ct-06 el RAG le hizo mal: sin contexto lo resolvió, con contexto lo confunde.
3. **ct-07 export sigue siendo el muro** (0/7 en todos los modelos y modos): tarea de keys/dedup
   que ni el RL con 28 steps pudo.
4. Todos los `hit=True` → el retrieval encuentra las chunks; el cuello es razonamiento, no recuperación.

## Notas técnicas del pipeline (para la próxima)
- El export GGUF corre el converter en un subproceso cuyo `sys.path[0]` es el dir del script
  de unsloth → el `sitecustomize.py` del lab NO se carga ahí. Correr con
  `PYTHONPATH=D:\ai-lab\fase2` para heredar los shims (sin eso: `AutoTokenizer` no importa).
- `run_code_rag.py` requiere cwd = `rag/` (busca `data/chunks.json` relativo).
- Merge RL: base = `merged_qwen35_attn` (el adapter apunta a ese dir), no a la base HF original.
- Artifacts: `merged_qwen35_attn_rl/` (18 GB bf16), `gguf_qwen35_attn_rl_gguf/` (5.78 GB + mmproj),
  `out_grpo/adapter_rl` (35 MB), `Modelfile.rl`.

## Qué seguiría
- Más señal: reward por partes (compile + tests individuales) o tasks más fáciles de aterrizar
  temprano, más steps, o lr más alto con KL más laxa.
- Apuntar explícitamente a ct-07 (keys/export): es donde hay más terreno para ganar.