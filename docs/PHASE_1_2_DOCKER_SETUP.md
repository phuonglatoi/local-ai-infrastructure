# PHASE 1-2: DOCKER INFRASTRUCTURE SETUP

## Tong quan

Phase nay bao gom:
- **Phase 1** (Day 1-10): Cai dat phan cung, GPU driver, Docker Engine
- **Phase 2** (Day 11-20): Trien khai cac AI services bang Docker Compose

## Ket qua mong doi

Sau khi hoan thanh, ban se co:
- Docker Engine + Docker Compose hoat dong tren Ubuntu Server
- NVIDIA Container Toolkit cho phep containers truy cap GPU
- Toan bo AI stack chay trong Docker containers:
  - Ollama (LLM Serving) tren port 11434
  - Open WebUI (Chat) tren port 8080
  - N8N (Workflow Automation) tren port 5678
  - Supabase (Database) tren port 8000/5432
  - SearXNG (Search) tren port 8888

---

## Buoc 1: Chuan bi Ubuntu Server

### 1.1 Cap nhat he dieu hanh

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git nano htop
```

### 1.2 Kiem tra thong tin he thong

```bash
# Kiem tra OS
lsb_release -a

# Kiem tra RAM
free -h

# Kiem tra disk
df -h

# Kiem tra GPU (neu da cai driver)
lspci | grep -i nvidia
```

---

## Buoc 2: Cai dat NVIDIA GPU Driver & CUDA

> **Chi ap dung cho server co GPU NVIDIA** (RTX 3090/4090/5090 hoac DGX Spark)

### 2.1 Cai dat NVIDIA Driver

```bash
# Them NVIDIA repository
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

# Hoac cai phien ban cu the
# sudo apt install -y nvidia-driver-560

# Khoi dong lai
sudo reboot
```

### 2.2 Verify GPU

```bash
nvidia-smi
```

Ket qua mong doi:
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 560.xx       Driver Version: 560.xx       CUDA Version: 13.x                |
|                                                                                         |
| GPU  Name          Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC          |
| Fan  Temp   Perf   Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M.           |
|   0  NVIDIA GeForce RTX 4090  Off | 00000000:01:00.0 Off |                  Off          |
|  0%   35C    P8    15W / 450W |      0MiB / 24576MiB |      0%      Default            |
+-----------------------------------------------------------------------------------------+
```

### 2.3 Cai dat CUDA Toolkit (Optional)

```bash
# Chi can thiet neu muon compile CUDA code tren host
# Docker containers da co CUDA san
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit
```

---

## Buoc 3: Cai dat Docker Engine

### 3.1 Cai dat Docker

```bash
# Go bo phien ban cu (neu co)
sudo apt remove -y docker docker-engine docker.io containerd runc

# Cai dat dependencies
sudo apt install -y ca-certificates curl gnupg

# Them Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Them Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Cai dat Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Cho phep user hien tai dung Docker khong can sudo
sudo usermod -aG docker $USER
newgrp docker
```

### 3.2 Verify Docker

```bash
docker --version
docker compose version
docker run hello-world
```

---

## Buoc 4: Cai dat NVIDIA Container Toolkit

> **Bat buoc** de Docker containers truy cap duoc GPU

### 4.1 Cai dat nvidia-container-toolkit

```bash
# Them NVIDIA Container Toolkit repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Cai dat
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Cau hinh Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 4.2 Verify GPU trong Docker

```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

Neu thay output `nvidia-smi` tuong tu nhu tren host -> GPU passthrough thanh cong!

---

## Buoc 5: Clone Project va Cau hinh

### 5.1 Clone repository

```bash
cd ~
git clone https://github.com/phuonglatoi/local-ai-infrastructure.git
cd local-ai-infrastructure
```

### 5.2 Tao file .env

```bash
cp .env.example .env
```

### 5.3 Generate secrets

```bash
# Tao cac secret ngau nhien
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env
echo "N8N_USER_MANAGEMENT_JWT_SECRET=$(openssl rand -hex 32)" >> .env
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .env
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env
echo "WEBUI_SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

> **QUAN TRONG**: Mo file `.env` va kiem tra lai tat ca cac gia tri truoc khi chay.

### 5.4 Chinh sua .env

```bash
nano .env
```

Cac truong **bat buoc** phai thay doi:
- `POSTGRES_PASSWORD` - Mat khau Postgres
- `JWT_SECRET` - JWT secret cho Supabase (it nhat 32 ky tu)
- `ANON_KEY` - Supabase anonymous key
- `SERVICE_ROLE_KEY` - Supabase service role key
- `N8N_ENCRYPTION_KEY` - Ma hoa N8N
- `N8N_USER_MANAGEMENT_JWT_SECRET` - JWT cho N8N

---

## Buoc 6: Khoi dong Services

### 6.1 Chay voi GPU NVIDIA

```bash
python3 scripts/start_services.py --profile gpu-nvidia
```

### 6.2 Chay voi CPU (khong co GPU)

```bash
python3 scripts/start_services.py --profile cpu
```

### 6.3 Chay voi Caddy (Production)

```bash
python3 scripts/start_services.py --profile gpu-nvidia --environment public
```

---

## Buoc 7: Verify Services

### 7.1 Kiem tra containers

```bash
docker compose ps
```

Tat ca services phai co trang thai `Up` hoac `healthy`.

### 7.2 Kiem tra tung service

```bash
# Ollama
curl http://localhost:11434/api/version

# Open WebUI
curl -s http://localhost:8080 | head -5

# N8N
curl -s http://localhost:5678/healthz

# Supabase
curl -s http://localhost:8000

# SearXNG
curl -s http://localhost:8888
```

### 7.3 Pull model Ollama (neu init chua xong)

```bash
docker exec -it ollama ollama pull qwen2.5:7b-instruct-q4_K_M
docker exec -it ollama ollama pull nomic-embed-text

# Kiem tra models da pull
docker exec -it ollama ollama list
```

### 7.4 Test chat voi Ollama

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:7b-instruct-q4_K_M",
  "messages": [{"role": "user", "content": "Xin chao!"}],
  "stream": false
}'
```

---

## Buoc 8: Quan ly Services

### Xem logs

```bash
# Tat ca services
docker compose logs -f

# Service cu the
docker compose logs -f ollama
docker compose logs -f open-webui
docker compose logs -f n8n
```

### Dung services

```bash
docker compose --profile gpu-nvidia down
```

### Khoi dong lai

```bash
docker compose --profile gpu-nvidia restart
```

### Cap nhat images

```bash
docker compose --profile gpu-nvidia pull
docker compose --profile gpu-nvidia up -d
```

---

## Troubleshooting

### GPU khong duoc nhan dien trong Docker

```bash
# Kiem tra nvidia-container-toolkit
dpkg -l | grep nvidia-container-toolkit

# Kiem tra Docker runtime
docker info | grep -i runtime

# Restart Docker
sudo systemctl restart docker
```

### Container khong start

```bash
# Xem logs chi tiet
docker compose logs <service-name>

# Kiem tra port conflict
sudo lsof -i :8080
sudo lsof -i :5678
```

### Out of Memory (OOM)

```bash
# Kiem tra memory usage
docker stats

# Giam model size: dung quantized version
docker exec -it ollama ollama pull qwen2.5:7b-instruct-q4_K_M  # ~4.5GB
# thay vi
# docker exec -it ollama ollama pull qwen2.5:72b  # ~40GB
```

---

## Ready Check (Gate sang Phase tiep theo)

- [ ] Docker Engine va Docker Compose da cai dat thanh cong
- [ ] NVIDIA Container Toolkit hoat dong (docker run --gpus all nvidia-smi)
- [ ] Tat ca 5 services chay binh thuong (docker compose ps)
- [ ] Open WebUI truy cap duoc tai http://localhost:8080
- [ ] Ollama co the serve model va tra loi chat
- [ ] N8N Dashboard truy cap duoc tai http://localhost:5678
- [ ] Supabase Studio truy cap duoc tai http://localhost:8000
