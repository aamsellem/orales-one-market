# Orales One Market

A curated app store for the **Olares One** — the first Olares hardware device, packing an RTX 5090M, 96GB DDR5, and a 24-core Intel CPU into a compact form factor.

Every app here is hand-tuned for this exact hardware. No generic configs — just the fastest possible inference on 24GB of GDDR7.

> **One-click install.** Add the market source, and apps appear in your Olares Market alongside the official catalog.

## Apps

### LLM Inference

| App | Model | Speed | Details |
|-----|-------|-------|---------|
| **Qwen3.5 35B-A3B** | 35B params, 3B active (MoE) | **128+ t/s** | Unsloth UD-Q4_K_XL, llama.cpp b8284, flash attention, CUDA graph opt |
| **GLM-4.7-Flash** | 30B params, 3B active (MoE) | — | Same optimized stack, MLA attention |

Full-size MoE models running entirely on GPU at speeds that rival much smaller dense models.

### Voice & Audio

| App | Model | Features |
|-----|-------|----------|
| **Qwen3-TTS 1.7B** | Text-to-speech | 9 premium voices, zero-shot voice cloning from 3s of audio, 10 languages |

## Quick Start

Add this URL as a market source in **Olares Market > Settings > Add Source**:

```
https://orales-one-market.aamsellem.workers.dev
```

Apps show up within 5 minutes. Install like any other Olares app — models download automatically on first launch.

## How It Works

A single Cloudflare Worker serves the full Olares Market Source API. Each app is a Helm chart with GPU-optimized configs, packaged and deployed from this repo.

```bash
npm install
npm run dev              # Local dev (localhost:8787)
npm run deploy           # Deploy to Cloudflare Workers
```

### Adding an app

1. Create an app directory with `Chart.yaml`, `OlaresManifest.yaml`, and `templates/`
2. Add an icon in `icons/<app-name>.png`
3. Package: `helm package <app-dir> -d charts/`
4. Deploy: `npm run deploy`

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/appstore/hash?version=X` | Catalog hash for cache check |
| GET | `/api/v1/appstore/info?version=X` | Full catalog with app summaries |
| POST | `/api/v1/applications/info` | App details (batched by ID) |
| GET | `/api/v1/applications/{name}/chart?fileName=X` | Chart `.tgz` download |
| GET | `/icons/{name}.png` | App icon |

## Related

- [orales-market](https://github.com/aamsellem/orales-market) — Generic apps for any Olares hardware

## License

MIT
