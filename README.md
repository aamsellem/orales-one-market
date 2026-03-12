# Orales One Market

Custom [Olares](https://olares.com) Market source optimized for the **Olares One** device.

> RTX 5090M (24GB) + Core Ultra 9 275HX (24 cores) + 96GB DDR5

A single Cloudflare Worker that serves the full Market Source API — app catalog, chart downloads, and icons.

## Apps

| App | Model | Backend | Quant | Performance |
|-----|-------|---------|-------|-------------|
| llamacppqwen35a3bone | Qwen3.5 35B-A3B | llama.cpp b8284 | UD-Q4_K_XL | **128.75 t/s** |
| llamacppglm47flash | GLM-4.7-Flash 30B-A3B | llama.cpp b8284 | UD-Q4_K_XL | — |
| qwen3ttstone | Qwen3-TTS 1.7B | Gradio | BF16 | TTS + voice cloning |

## Setup

Add this URL as a market source in **Olares Market > Settings**:

```
https://orales-one-market.aamsellem.workers.dev
```

The market syncs every 5 minutes.

## Development

```bash
npm install
npm run dev              # Local dev server (localhost:8787)
npm run deploy           # Deploy to Cloudflare Workers
```

### Adding an app

1. Create an app directory at the repo root with `Chart.yaml`, `OlaresManifest.yaml`, and `templates/`
2. Add an icon in `icons/<app-name>.png`
3. Package: `helm package <app-dir> -d charts/`
4. Build & deploy: `npm run deploy`

The build script (`scripts/build-catalog.js`) scans app directories, packages charts and icons as base64, and generates the catalog served by the worker.

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
