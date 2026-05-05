# Local AI Infrastructure

> **De tai**: Thiet ke va Trien khai Ha tang Container hoa va Truy cap WAN An toan cho He thong Local AI

Ha tang Docker hoa toan bo he thong Local AI (Ollama, Open WebUI, N8N, Supabase, SearXNG, Caddy) va thiet lap truy cap tu xa an toan qua Tailscale VPN + Cloudflare Tunnel + Zero Trust.

## Kien truc He thong

```
                         INTERNET
                            |
           +----------------+----------------+
           |                                 |
     [Tailscale VPN]              [Cloudflare Tunnel]
     (Private Mesh)               (Public + Zero Trust)
           |                                 |
     +-----+-----+                      [Caddy]
     |           |                    Reverse Proxy
   [SSH]    [VS Code]                      |
                              +------+------+------+------+
                              |      |      |      |      |
                           [WebUI] [N8N] [Supa]  [Search] [Ollama]
                           :8080  :5678  :8000   :8888   :11434
                              |      |      |      |      |
                              +------+------+------+------+
                                   Docker Network
```

## Thanh phan

| Service | Muc dich | Port | Image |
|---------|----------|------|-------|
| **Ollama** | LLM Serving Engine | 11434 | `ollama/ollama` |
| **Open WebUI** | Chat Interface | 8080 | `ghcr.io/open-webui/open-webui` |
| **N8N** | Workflow Automation | 5678 | `n8nio/n8n` |
| **Supabase** | Database + Auth | 8000, 5432 | `supabase/postgres` |
| **SearXNG** | Private Search | 8888 | `searxng/searxng` |
| **Caddy** | Reverse Proxy + HTTPS | 80, 443 | `caddy:2-alpine` |

## Cau truc Project

```
local-ai-infrastructure/
├── README.md                           # File nay
├── docker-compose.yml                  # Docker Compose chinh
├── .env.example                        # Mau environment variables
├── caddy/
│   └── Caddyfile                       # Caddy reverse proxy config
├── supabase/
│   └── kong.yml                        # Supabase API Gateway config
├── searxng/
│   └── settings.yml                    # SearXNG search engine config
├── n8n/
│   └── backup/
│       └── workflows/                  # N8N workflow backups
├── scripts/
│   └── start_services.py              # Script khoi dong services
├── docs/
│   ├── DE_TAI_OUTLINE.md              # Outline de tai chi tiet
│   ├── PHASE_1_2_DOCKER_SETUP.md      # Huong dan Phase 1-2 (Docker)
│   └── PHASE_5_WAN_ACCESS.md          # Huong dan Phase 5 (WAN)
└── diagrams/                           # So do kien truc
```

## Yeu cau Phan cung

### Toi thieu
- CPU: 4 cores
- RAM: 16 GB
- Disk: 50 GB SSD
- OS: Ubuntu 22.04+

### Khuyen nghi (cho AI workloads)
- GPU: NVIDIA RTX 3090/4090/5090 hoac DGX Spark (GB10)
- RAM: 32-128 GB
- VRAM: 24 GB+
- Disk: 200 GB+ NVMe SSD

## Quick Start

### 1. Clone repository

```bash
git clone https://github.com/phuonglatoi/local-ai-infrastructure.git
cd local-ai-infrastructure
```

### 2. Cau hinh environment

```bash
cp .env.example .env
# Chinh sua .env voi cac secret cua ban
nano .env
```

### 3. Khoi dong (GPU NVIDIA)

```bash
python3 scripts/start_services.py --profile gpu-nvidia
```

### 4. Truy cap services

| Service | URL |
|---------|-----|
| Open WebUI | http://localhost:8080 |
| N8N | http://localhost:5678 |
| Supabase | http://localhost:8000 |
| SearXNG | http://localhost:8888 |
| Ollama API | http://localhost:11434 |

## Profiles

| Profile | Lenh | Ghi chu |
|---------|------|---------|
| NVIDIA GPU | `--profile gpu-nvidia` | Can nvidia-container-toolkit |
| AMD GPU | `--profile gpu-amd` | Can ROCm |
| CPU only | `--profile cpu` | Khong can GPU |

## Environments

| Environment | Lenh | Mo ta |
|-------------|------|-------|
| Private | `--environment private` | (Mac dinh) Tat ca ports accessible |
| Public | `--environment public` | Chi port 80/443, traffic qua Caddy |

## Tai lieu Chi tiet

| Phase | Tai lieu | Mo ta |
|-------|---------|-------|
| Phase 1-2 | [PHASE_1_2_DOCKER_SETUP.md](docs/PHASE_1_2_DOCKER_SETUP.md) | Cai dat Docker, GPU, trien khai AI stack |
| Phase 5 | [PHASE_5_WAN_ACCESS.md](docs/PHASE_5_WAN_ACCESS.md) | Tailscale VPN, Cloudflare Tunnel, Zero Trust |
| Outline | [DE_TAI_OUTLINE.md](docs/DE_TAI_OUTLINE.md) | Outline de tai day du |

## Tham khao

- [coleam00/local-ai-packaged](https://github.com/coleam00/local-ai-packaged) - Repo goc tham khao
- [NVIDIA DGX Spark](https://build.nvidia.com/spark) - Phan cung AI on-premise
- [Ollama](https://ollama.com/) - Local LLM serving
- [Open WebUI](https://openwebui.com/) - Chat interface
- [N8N](https://n8n.io/) - Workflow automation
- [Supabase](https://supabase.com/) - Database & Auth
- [Tailscale](https://tailscale.com/) - Mesh VPN
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) - Secure tunneling
- [Caddy](https://caddyserver.com/) - Reverse proxy

## License

Apache License 2.0
