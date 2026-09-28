# Fase 3b — GRPO con reward denso (assert-coverage) vs reward binario

**Modelo**: Qwen3.5 (SFT fundido `merged_qwen35_attn`) + LoRA RL attention-only (r16, alpha 16)
**Hardware**: RX 9070 XT 16 GB (ROCm Windows, sin distributed → shims en sitecustomize)
**Config**: `--g 3 --max-comp 1536 --seq 3072 --temp 0.8 --lr 2e-5 --warmup 2 --save 7 --bf16 --seed 7`
**Réplica exacta** del run Fase 3 salvo el reward → comparación limpia.

## Hipótesis

El reward binario 0/1 tiraba la señal de los "casi": ct-02 tenía 0.60 de coverage
(3/5 asserts) y recibía 0 como si fuera un completo fracaso. Con assert-coverage
(fracción de asserts del test que pasan; SQL = fracción de filas esperadas
coincidentes) cada acierto parcial genera gradiente → el modelo aprende la
estructura antes de aterrizar el 100%.

## Reward denso (`reward_score.py`)

- **Python/SQL**: AST sobre los asserts del test → `result[assert]` de la
  generación vs `expected[assert]`; coverage = hits / total asserts.
- **Regla del dominio intacta**: el prompt NUNCA ve los tests ni los criterios;
  el reward sí.
- Flag `--reward dense|binary` (default dense) en `train_grpo.py`.

## Curva de entrenamiento

### Fase 3 (binario) — 28 steps
- Steps con reward > 0: **8/28**
- Mejor reward: **0.3333** (step 8)
- Señal fina (0 < r < 0.2): escasa

### Fase 3b (dense) — 25 steps + resume 7 (checkpoint-21)
- Steps con señal densa: **~15/25** (run cortado) + 2/7 (resume)
- Mejor reward: **0.3889** (step 14)
- Señal fina abundante: 0.083, 0.104, 0.111, 0.125, 0.208 ...
- KL 0.00025 → 0.00051 (sin divergencia); VRAM estable 9 GB, pico 15.26 GB

| Métrica | Binario | Denso |
|---|---|---|
| Steps 5+ con señal | ~7/21 (33%) | ~15/21 (71%) |
| Reward máximo | 0.333 | **0.389** |
| Señal fraccional <0.2 | casi nula | abundante |

## Incidente de ejecución (documentado en el lab)

El run completo de 28 steps se cortó a 25/28 SIN crash de entrenamiento: el
proceso corría como hijo del shell de opencode y un **restart del server (por
actualización)** lo mató. Recuperación:

1. Nuevo flag `--adapter <dir>` en `train_grpo.py`: carga un LoRA existente y
   continúa el entrenamiento (en vez de re-correr 1.5 h desde cero).
2. Resume desde `checkpoint-21` + 7 steps → equivalente al run de 28 completo.
3. Lanzamiento **desacoplado** (via `Start-Process` de PowerShell, no es hijo
   del shell) → los próximos runs sobreviven a restarts del server.

## Despliegue (pipeline RL2)

1. `merge_rl2.py` → `merged_qwen35_attn_rl2` (bf16, 4 shards) ✅
2. `to_gguf_rl2.py` (requiere `PYTHONPATH=D:/ai-lab/fase2`, fix documentado) →
   Q4_K_M
3. `ollama create local-qwen-rl2` (Modelfile.rl2)
4. Eval del puente → tabla vs Fase 3 (pendiente)

## Resultados del puente

Eval: `run_code_rag.py --model local-qwen-rl2:latest` (cwd `D:\ai-lab\rag`).
**Alta varianza de muestreo** (temp 0.6): el RL2 "coquetea" con varios tests —
se reportan 2 runs y la capacidad (alguna vez PASS).

| Test | RL bin sin RAG | RL bin con RAG | RL2 (run1) sin/con RAG | RL2 (run2) sin/con RAG | Capacidad |
|---|---|---|---|---|---|
| ct-01 | ❌ | ✅ | ❌/✅ | ❌/✅ | ✅ ✅ |
| ct-02 | ❌ | ❌ | ❌/❌ | ❌/❌ | ❌ (1 línea) |
| ct-03 | ❌ | ✅ | ❌/✅ | ❌/❌ | ⚠️ frecuente |
| ct-04 | ❌ | ✅ | ❌/✅ | ❌/❌ | ⚠️ frecuente |
| ct-05 | ❌ | ✅ | ❌/✅ | ❌/✅ | ✅ |
| ct-06 | ✅ | ❌ | ❌/❌ | ✅/✅ | ⚠️ **nuevo** |
| ct-07 | ❌ | ❌ | ❌/**✅** | ❌/❌ | ⚠️ **¡se rompió el muro!** |
| **Total** | 2/7 | 4/7 | 0/7 / **5/7** | 1/7 / 3/7 | **sin RAG 2/7 · con RAG 7/7 posibles** |

### Lectura
- **ct-07 por primera vez en la historia del lab** (PASS con RAG en run 1): el reward
  denso + el chunk de `07-RECONCILIATION.md` en el RAG hicieron el trabajo. En el peor
  muestreo falla por **una sola clave** (`Estado: 'unidentified'` vs `'conciliated'`)
  con las otras 8 exactas (incl. `Aplicación` con acento y `Tipo: 'Abono'`).
- **ct-06**: ahora pasa sin RAG Y con RAG (antes solo el binario lo pasaba sin RAG y
  con RAG le jugaba en contra). El dense integró el contexto.
- **ct-02**: estructura correcta; dos causas de fallo distintas (artefacto de entorno
  `holidays` + parseo de fechas con `.date()` sobre strings).
- **ct-03/ct-04**: inestables (PASS en 1 de 2 runs) — cercanos pero no consolidados.

### Fix del lab (entornos de verificación)
- `holidays` no estaba instalado ni en el python del eval ni en `fase2/.venv` →
  el RL2 lo usaba legítimamente (el motor real del dominio lo usa) y el test moría
  con `ModuleNotFoundError`. Instalado en ambos (v0.105).
- Pendiente: documentar dependencias del eval en un `requirements*.txt` de `rag/`.

## Recomendación Fase 3c
1. Más steps de RL dense (consolidar la señal de ct-02/03/04/07 que ya está "casi").
2. Bajar temp del eval (0.6 → 0.3) para reducir la varianza de muestreo en el reporte,
   o evaluar con N runs y reportar mediana/máximo.
3. Verificar el chunk de `07-RECONCILIATION.md` entra en el retrieve de ct-07 (ya
   confirmado: hit=True → docs/07-RECONCILIATION.md) y qué tan arriba queda.

## Hallazgo clave — ct-07 es atacable

El formato exacto de ct-07 (columnas `Tipo/Fecha/Monto/Estado/Cliente/Aplicación`
con acento, `credit→Abono`, `debit→Cargo`) está **100% documentado** en
`docs/07-RECONCILIATION.md` (chunk del RAG): el JS del motor de reconciliación
mapea exactamente esas claves. Los fallos del RL fueron por una línea pedante
(`strftime` sobre string `date`) y, sin RAG, por keys en minúscula — no por
desconocimiento del formato. Pendiente: confirmar que el retrieve trae ese chunk
en el eval con RAG.