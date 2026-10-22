# Runtime Environment Info

Runtime environment for the recent local capsule-maker LLM tests (Qwen3.8-27B on a local llama-server, driven by the OpenCode harness). Test artefacts live in this directory: `conversation-log.md`, `question-sheet.md`, `phase2-job-report.md`, `phase2_6a/`, `capsule-portability-qwen-oc/`, `session-capsule/`, `tx_nlcc/`.

## Hardware

- Ryzen 9 5900X (12C/24T) + 64GB DDR4 3600 MT/s
- RTX 3090 (24GB GDDR6X VRAM) (250W power limit)
- GPU driver 615.71.10 (CUDA UMD 13.4); CUDA 13 runtime (`libcudart.so.13`)

## Software

- OS: Debian GNU/Linux 13 (trixie), kernel 7.0.14-25-pve
- Harness: Opencode v2.0.29 (provider policy: `llama.cpp` allowed, all other providers denied)
- capsule-maker 0.1.0a1 (repo HEAD `65942fa`), Python 3.13.5
- Model: Qwen3.8-27B-UD-Q3_K_XL.gguf (13 GB, Q3_K_XL "Unsloth Dynamic" quantization), `/ssd/models/qwen3.8/`

### Inference

- llama.cpp build 10976 (commit hash `9e71716247113b47bb831d1e0680cbf5f242f094`, short `9e7171624`, built 2026-09-15)
- Build config: Release, `GGML_CUDA=ON`, CUDA flash attention ON (q4_0/q8_0/f16/bf16), AVX off, no BLAS
- Binary: `/home/ljbeal/llama.cpp/build/bin/llama-server`
- Context: 200,000 tokens; KV cache quantized q8_0 (K and V)
- Sampling: temp 1.0, top-p 0.95, top-k 20, min-p 0.0
- Multimodal projector: `mmproj-BF16.gguf` (889 MB)
