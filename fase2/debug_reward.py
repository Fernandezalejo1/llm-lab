#!/usr/bin/env python3
"""Valida la reward del GRPO (make_reward / verify_task) con completions
sabidas-correctas de la eval de Fase 2, usando el flujo EXACTO de trl 0.24
(completions + reward_kwargs con la columna 'task' del dataset)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fase2"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rag"))

# remake del make_reward de train_grpo (sin imports pesados)
import concurrent.futures as cf
import tempfile

from run_code_rag import verify_task  # noqa: E402


def completion_text(completion):
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list):
        return "".join(m.get("content", "") for m in completion if isinstance(m, dict))
    return str(completion)


def make_reward():
    def reward_fn(prompts, completions, completion_ids=None, **reward_kwargs):
        tasks = reward_kwargs.get("task", [])
        out = [0.0] * len(completions)
        def _check(k):
            task = (tasks[k] if tasks is not None and k < len(tasks) else None)
            if task is None:
                return k, 0.0, "sin task"
            with tempfile.TemporaryDirectory() as td:
                ok, err = verify_task(task, completion_text(completions[k]), Path(td))
            return k, 1.0 if ok else 0.0, err
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            for k, r, e in ex.map(_check, range(len(completions))):
                out[k] = r
        return out
    return reward_fn


def main():
    tasks = [json.loads(l) for l in open(
        Path(__file__).resolve().parent.parent / "rag" / "code_tasks.jsonl",
        encoding="utf-8") if l.strip()]

    # completions sabidas: la respuesta con RAG que PASÓ en la eval de Fase 2
    evals = sorted(Path(__file__).resolve().parent.parent.glob(
        "results/code_rag_*.jsonl"))
    bank = {}  # task_id -> completions reales con pass_rag/pass_base
    for ef in evals:
        for line in open(ef, encoding="utf-8"):
            r = json.loads(line)
            if "id" not in r:
                continue
            bank.setdefault(r["id"], []).append(
                (r.get("pass_rag", False), r.get("ans_rag", "")))
            bank.setdefault(r["id"], []).append(
                (r.get("pass_base", False), r.get("ans_base", "")))

    reward = make_reward()
    print("tareas:", len(tasks), flush=True)
    n_ok = 0
    for t in tasks:
        best = bank.get(t["id"], [])
        ok_ans = [a for ok, a in best if ok]
        if not ok_ans:
            print(f"  {t['id']}: (sin respuesta PASS en evals para probar)", flush=True)
            continue
        # flujo trl: prompts alineados 1:1 con completions; task vía reward_kwargs
        prompts = [t["prompt"]] * len(ok_ans)
        res = reward(prompts, ok_ans, task=[t] * len(ok_ans))
        print(f"  {t['id']}: reward={res} sobre {len(ok_ans)} completions PASS", flush=True)
        n_ok += sum(1 for x in res if x > 0)

    # caso negativo control: tarea A con respuesta de tarea B
    print("\ncontrol negativo (tarea cruzada):", flush=True)
    a, b = tasks[0], tasks[1]
    res = reward([a["prompt"]], [b["prompt"]], task=[a])
    print(f"  reward(ct-01 con texto de ct-02) = {res}", flush=True)

    # caso 'task=[]' (alineación rota -> siempre 0)
    print("\ncontrol alineación (sin task en kwargs):", flush=True)
    res = reward([tasks[0]["prompt"]], ["respuesta cualquiera"], task=None)
    print(f"  reward sin task = {res} (0 esperado)", flush=True)


if __name__ == "__main__":
    main()