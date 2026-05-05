# DE TAI: Thiet ke va Trien khai Ha tang Container hoa va Truy cap WAN An toan cho He thong Local AI

## OUTLINE CHI TIET

---

## Chuong 1: Gioi thieu

### 1.1 Dat van de
- Xu huong trien khai AI on-premise (Local AI) thay vi Cloud de bao mat du lieu va giam chi phi.
- Thach thuc: Quan ly nhieu dich vu AI (LLM, Database, Workflow Engine, UI) tren cung mot server.
- Nhu cau truy cap tu xa an toan ma khong expose port truc tiep ra Internet.

### 1.2 Muc tieu de tai
1. **Docker**: Container hoa toan bo AI stack (Ollama, Open WebUI, N8N, Supabase, Caddy, SearXNG) thanh mot he thong dong nhat, de trien khai va quan ly.
2. **WAN Access**: Thiet lap truy cap tu xa an toan qua Tailscale VPN va Cloudflare Tunnel + Zero Trust.

### 1.3 Pham vi de tai
- **Trong pham vi**: Docker Compose, NVIDIA Container Toolkit, Caddy reverse proxy, Tailscale VPN, Cloudflare Tunnel/Zero Trust.
- **Ngoai pham vi**: Huan luyen mo hinh AI, xay dung Agent logic (Phase 3-4), thuong mai hoa (Phase 6).

### 1.4 Phuong phap nghien cuu
- Nghien cuu tai lieu: Docker docs, NVIDIA Container Toolkit, Tailscale, Cloudflare Zero Trust.
- Thuc nghiem: Trien khai thuc te tren server Ubuntu voi GPU NVIDIA.
- Kiem thu: Verify kha nang truy cap tu xa, bao mat, hieu suat.

---

## Chuong 2: Co so ly thuyet

### 2.1 Container hoa voi Docker
- 2.1.1 Docker Engine va Docker Compose
- 2.1.2 Docker Networking (Bridge, Host, Overlay)
- 2.1.3 Docker Volumes va Data Persistence
- 2.1.4 Multi-service orchestration voi Docker Compose
- 2.1.5 Health Checks va Restart Policies

### 2.2 GPU Passthrough cho AI Workloads
- 2.2.1 NVIDIA Container Toolkit (nvidia-ctk)
- 2.2.2 CUDA trong Docker containers
- 2.2.3 GPU resource allocation va sharing

### 2.3 Cac thanh phan AI Stack
- 2.3.1 Ollama - LLM Serving Engine
- 2.3.2 Open WebUI - Giao dien chat
- 2.3.3 N8N - Workflow Automation Platform
- 2.3.4 Supabase - Database & Auth (PostgreSQL)
- 2.3.5 SearXNG - Private Search Engine
- 2.3.6 Caddy - Reverse Proxy voi Auto-HTTPS

### 2.4 Mang rieng ao (VPN) va Zero Trust
- 2.4.1 Tailscale - Mesh VPN (WireGuard-based)
- 2.4.2 Cloudflare Tunnel - Secure Tunneling
- 2.4.3 Cloudflare Zero Trust - Identity-aware Access
- 2.4.4 So sanh VPN truyen thong vs Mesh VPN vs Zero Trust

---

## Chuong 3: Phan tich va Thiet ke he thong

### 3.1 Kien truc tong the
```
[Internet/WAN]
       |
[Cloudflare Tunnel] --> [Caddy Reverse Proxy]
       |                        |
[Tailscale VPN]          +------+--------+--------+--------+
       |                 |      |        |        |        |
   [SSH/Dev]          [WebUI] [N8N]  [Supabase] [Ollama] [SearXNG]
                      :8080   :5678   :8000     :11434   :8888
```

### 3.2 Thiet ke Docker Infrastructure
- 3.2.1 So do container va moi quan he giua cac service
- 3.2.2 Network topology: Internal network vs External exposure
- 3.2.3 Volume mapping va data persistence strategy
- 3.2.4 Environment variables va secrets management
- 3.2.5 GPU allocation strategy (NVIDIA profiles)

### 3.3 Thiet ke WAN Access Layer
- 3.3.1 Lop Private: Tailscale Mesh VPN cho Developer Access
- 3.3.2 Lop Public Auth: Cloudflare Tunnel + Zero Trust cho End Users
- 3.3.3 Caddy: Reverse proxy dieu phoi traffic den cac Docker services
- 3.3.4 SSL/TLS certificate management (Auto-HTTPS)

### 3.4 Thiet ke bao mat
- 3.4.1 Network segmentation (Docker internal network)
- 3.4.2 Zero Trust policies (Email domain restriction, OTP)
- 3.4.3 SSH key-based authentication
- 3.4.4 Firewall rules (UFW configuration)

---

## Chuong 4: Trien khai (Implementation)

### 4.1 Chuan bi moi truong
- 4.1.1 Cai dat Ubuntu Server
- 4.1.2 Cai dat Docker Engine va Docker Compose
- 4.1.3 Cai dat NVIDIA Driver + CUDA + NVIDIA Container Toolkit
- 4.1.4 Verify GPU access: nvidia-smi

### 4.2 Trien khai Docker AI Stack
- 4.2.1 Cau truc project va docker-compose.yml
- 4.2.2 Cau hinh environment variables (.env)
- 4.2.3 Khoi dong services theo profiles (gpu-nvidia, gpu-amd, cpu)
- 4.2.4 Verify tung service hoat dong
- 4.2.5 Pull models voi Ollama

### 4.3 Trien khai Caddy Reverse Proxy
- 4.3.1 Cau hinh Caddyfile cho local va production
- 4.3.2 Mapping domain -> container port
- 4.3.3 Auto-HTTPS voi Let's Encrypt

### 4.4 Trien khai Tailscale VPN
- 4.4.1 Cai dat Tailscale tren Server
- 4.4.2 Cai dat Tailscale tren Client
- 4.4.3 Cau hinh MagicDNS
- 4.4.4 Test SSH qua Tailscale

### 4.5 Trien khai Cloudflare Tunnel & Zero Trust
- 4.5.1 Cai dat cloudflared daemon
- 4.5.2 Tao Tunnel va routing DNS
- 4.5.3 Cau hinh Zero Trust Access Policies
- 4.5.4 Tich hop voi Caddy

---

## Chuong 5: Kiem thu va Danh gia

### 5.1 Kiem thu chuc nang
- 5.1.1 Verify tat ca Docker services khoi dong thanh cong
- 5.1.2 Verify Ollama co the serve models
- 5.1.3 Verify Open WebUI giao tiep voi Ollama
- 5.1.4 Verify N8N ket noi Supabase va Ollama

### 5.2 Kiem thu WAN Access
- 5.2.1 Test Tailscale VPN tu mang ngoai
- 5.2.2 Test Cloudflare Tunnel + Zero Trust login
- 5.2.3 Test VS Code Remote-SSH qua Tailscale
- 5.2.4 Test latency va throughput

### 5.3 Kiem thu bao mat
- 5.3.1 Verify Zero Trust chan truy cap trai phep
- 5.3.2 Verify khong co port nao bi expose truc tiep
- 5.3.3 Port scanning test

### 5.4 Kiem thu hieu suat
- 5.4.1 GPU utilization khi chay inference
- 5.4.2 Memory usage cua Docker containers
- 5.4.3 Response time cua API qua VPN vs Direct

---

## Chuong 6: Ket luan va Huong phat trien

### 6.1 Ket qua dat duoc
- Tong hop ket qua trien khai va kiem thu.

### 6.2 Han che
- Phu thuoc vao phan cung GPU.
- Bandwidth gioi han khi truy cap qua VPN.

### 6.3 Huong phat trien
- Tich hop voi Phase 3 (RAG) va Phase 4 (AI Agents).
- Mo rong thanh Kubernetes cluster.
- Toi uu hoa quantization cho cac mo hinh lon hon.

---

## Phu luc
- A: Ma nguon docker-compose.yml day du
- B: Cau hinh Caddyfile
- C: Script tu dong hoa (start_services.py)
- D: Cau hinh Tailscale va Cloudflare
- E: Ket qua benchmark hieu suat
