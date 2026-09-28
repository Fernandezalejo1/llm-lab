import json

rows = []
with open("out_grpo/rewards.jsonl") as f:
    for line in f:
        d = json.loads(line)
        lg = d.get("logs", {})
        if "kl" in lg and "reward" in lg:
            rows.append(d)

zero = [r["step"] for r in rows if r["logs"]["reward"] < 1e-4]
pos = [(r["step"], round(r["logs"]["reward"], 4)) for r in rows if r["logs"]["reward"] >= 1e-4]
print("steps con metricas:", len(rows))
print("reward 0:", zero)
print("reward > 0:", pos)

k = [r["logs"]["kl"] for r in rows]
l = [r["logs"]["completions/mean_length"] for r in rows]
t = [r["logs"]["completions/mean_terminated_length"] for r in rows]
print("KL min %.6f max %.6f" % (min(k), max(k)))
print("mean_length min %.0f max %.0f" % (min(l), max(l)))
print("mean_terminated min %.0f max %.0f" % (min(t), max(t)))

for r in rows:
    print("step %2d | reward %.4f | kl %.5f | len %.0f | term %.0f" % (
        r["step"], r["logs"]["reward"], r["logs"]["kl"],
        r["logs"]["completions/mean_length"],
        r["logs"]["completions/mean_terminated_length"]))