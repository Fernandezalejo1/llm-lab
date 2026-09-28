@echo off
cd /d D:\ai-lab\fase2
D:\ai-lab\fase2\.venv\Scripts\python.exe train_grpo.py --adapter out_grpo_dense/checkpoint-21 --steps 7 --g 3 --max-comp 1536 --seq 3072 --temp 0.8 --reward dense --out out_grpo_dense_resume > grpo_dense_resume.log 2>&1