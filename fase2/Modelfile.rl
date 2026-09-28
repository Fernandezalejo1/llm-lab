FROM D:/ai-lab/fase2/gguf_qwen35_attn_rl_gguf/merged_qwen35_attn_rl.Q4_K_M.gguf

# GGUF del modelo GRPO-RL (Fase 3). Template de chat Qwen3.5 embebido.
# Params del lab (mismos que local-qwen:latest y local-qwen-ft para
# comparación limpia entre baselina / FT / RL):
PARAMETER temperature 0.6
PARAMETER top_p 0.9
PARAMETER num_ctx 32768