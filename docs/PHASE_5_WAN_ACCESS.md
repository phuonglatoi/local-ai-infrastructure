# PHASE 5: TRUY CAP WAN AN TOAN (SECURE REMOTE ACCESS)

## 1. Tong quan

### Muc tieu
Thiet lap kha nang truy cap he thong Local AI tu xa qua Internet (WAN) ma khong can dung Cloud cong cong, dam bao tinh bao mat tuyet doi cho du lieu va mo hinh.

### Ket qua mong doi
- Nguoi dung co the truy cap Open WebUI, N8N va SSH vao server tu bat cu dau
- 2 lop bao ve: VPN rieng tu (Tailscale) va xac thuc Zero Trust (Cloudflare)
- Khong can mo port tren router, khong co Public IP

### Prerequisites
- Da hoan thanh Phase 1-2: Tat ca Docker services dang chay on dinh
- 01 tai khoan Tailscale (mien phi tai https://tailscale.com)
- 01 tai khoan Cloudflare (mien phi tai https://cloudflare.com)
- 01 ten mien da tro Nameserver ve Cloudflare

---

## 2. Kien truc WAN Access Layer

```
                        INTERNET
                           |
          +----------------+----------------+
          |                                 |
    [Tailscale VPN]              [Cloudflare Tunnel]
    (Mesh Private)               (Public + Zero Trust)
          |                                 |
    +-----+-----+                     [cloudflared]
    |           |                           |
  [SSH]    [VS Code]                   [Caddy Reverse Proxy]
  Remote    Remote                          |
                              +------+------+------+------+
                              |      |      |      |      |
                           [WebUI] [N8N] [Supa] [Search] [Ollama]
                           :8080  :5678  :8000  :8888   :11434
```

### 2 lop bao ve:

| Lop | Cong nghe | Muc dich | Doi tuong |
|-----|-----------|----------|-----------|
| **Private** | Tailscale | Mesh VPN, SSH, Dev tools | Ky thuat vien, Developer |
| **Public Auth** | Cloudflare Tunnel + Zero Trust | Expose WebUI qua domain, xac thuc OTP | End Users, Quan ly |

---

## 3. LOP 1: Tailscale (Truy cap Noi bo Tu xa)

### 3.1 Tailscale la gi?

Tailscale tao ra mot mang VPN dang Mesh (peer-to-peer) dua tren WireGuard:
- Moi thiet bi duoc cap 1 IP rieng (100.x.x.x)
- Ket noi truc tiep P2P, khong qua server trung gian
- Khong can mo port, khong can Public IP
- MagicDNS: Truy cap bang hostname thay vi IP

### 3.2 Cai dat tren AI Server

```bash
# Cai dat Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Kich hoat va dang nhap
sudo tailscale up

# Lay IP Tailscale cua server
tailscale ip -4
# Output: 100.x.x.x
```

### 3.3 Cai dat tren Client (Laptop/Mac)

1. Tai Tailscale tu https://tailscale.com/download
2. Cai dat va dang nhap cung tai khoan
3. Verify ket noi:

```bash
# Tren Client, ping server
ping 100.x.x.x  # IP Tailscale cua server

# Hoac dung MagicDNS
ping ai-server   # Hostname cua server trong Tailscale
```

### 3.4 Cau hinh MagicDNS

1. Truy cap https://login.tailscale.com/admin/dns
2. Bat "MagicDNS"
3. Gio co the truy cap server bang hostname:
   - `http://ai-server:8080` -> Open WebUI
   - `http://ai-server:5678` -> N8N
   - `ssh user@ai-server` -> SSH

### 3.5 SSH qua Tailscale

```bash
# Tu Client, SSH vao server
ssh user@100.x.x.x

# Hoac dung MagicDNS
ssh user@ai-server

# Voi VS Code Remote-SSH:
# 1. Cai extension "Remote - SSH" trong VS Code
# 2. Ctrl+Shift+P -> "Remote-SSH: Connect to Host..."
# 3. Nhap: user@ai-server
# 4. Chon Linux -> Nhap password
```

### 3.6 NVIDIA Sync (cho DGX Spark/GX10)

Neu dung NVIDIA DGX Spark hoac GX10:
1. Mo NVIDIA Sync application
2. Nhap Hostname: `ai-server` (MagicDNS) hoac IP Tailscale
3. Cau hinh SSH key
4. Quan ly Playbooks va development tools tu xa

---

## 4. LOP 2: Cloudflare Tunnel + Zero Trust

### 4.1 Tai sao can Cloudflare Tunnel?

- Tailscale yeu cau cai app tren moi thiet bi -> khong tien cho end users
- Cloudflare Tunnel cho phep truy cap qua trinh duyet binh thuong
- Zero Trust them lop xac thuc (Email/OTP) truoc khi cho truy cap

### 4.2 Cai dat cloudflared tren Server

```bash
# Tai va cai dat cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

# Verify
cloudflared --version
```

### 4.3 Xac thuc va Tao Tunnel

```bash
# Dang nhap Cloudflare (se mo trinh duyet)
cloudflared tunnel login
# -> Chon ten mien can quan ly

# Tao tunnel
cloudflared tunnel create local-ai-tunnel
# -> Ghi lai Tunnel ID duoc tao ra

# Xem danh sach tunnels
cloudflared tunnel list
```

### 4.4 Cau hinh Tunnel

Tao file cau hinh:

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Noi dung `config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/<user>/.cloudflared/<TUNNEL_ID>.json

ingress:
  # Open WebUI
  - hostname: ai.yourdomain.com
    service: http://localhost:8080

  # N8N Workflow
  - hostname: n8n.yourdomain.com
    service: http://localhost:5678

  # Supabase
  - hostname: db.yourdomain.com
    service: http://localhost:8000

  # SearXNG
  - hostname: search.yourdomain.com
    service: http://localhost:8888

  # Catch-all (bat buoc, phai o cuoi)
  - service: http_status:404
```

> **Luu y**: Thay `<TUNNEL_ID>`, `<user>`, va `yourdomain.com` bang gia tri thuc te.

### 4.5 Routing DNS

```bash
# Tro subdomain ve tunnel
cloudflared tunnel route dns local-ai-tunnel ai.yourdomain.com
cloudflared tunnel route dns local-ai-tunnel n8n.yourdomain.com
cloudflared tunnel route dns local-ai-tunnel db.yourdomain.com
cloudflared tunnel route dns local-ai-tunnel search.yourdomain.com
```

### 4.6 Chay Tunnel

```bash
# Test thu
cloudflared tunnel run local-ai-tunnel

# Cai dat nhu system service (auto-start khi boot)
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Kiem tra trang thai
sudo systemctl status cloudflared
```

---

## 5. Cau hinh Cloudflare Zero Trust

### 5.1 Tao Access Application

1. Truy cap https://one.dash.cloudflare.com
2. Vao **Access** -> **Applications** -> **Add an Application**
3. Chon **Self-hosted**
4. Dien thong tin:
   - **Application name**: Local AI WebUI
   - **Session Duration**: 24 hours
   - **Application domain**: `ai.yourdomain.com`

### 5.2 Tao Access Policy

1. Trong Application vua tao, tab **Policies**
2. **Add a policy**:
   - **Policy name**: Company Email Only
   - **Action**: Allow
   - **Include rule**:
     - Selector: `Emails ending in`
     - Value: `@ten-cong-ty.com`
3. Save

### 5.3 Cau hinh OTP Authentication

1. Vao **Settings** -> **Authentication**
2. Trong **Login methods**, them:
   - **One-time PIN** (OTP qua Email) - Mac dinh, khong can cau hinh them
   - (Optional) **Google** - Dang nhap bang Google Account

### 5.4 Tao Application cho N8N

Lap lai buoc 5.1-5.2 cho:
- `n8n.yourdomain.com` - N8N Workflow
- `db.yourdomain.com` - Supabase Dashboard

---

## 6. Cau hinh Caddy (Khi dung voi Cloudflare Tunnel)

Neu ban dung Cloudflare Tunnel truc tiep den cac port (nhu trong config.yml o buoc 4.4), ban **khong bat buoc** can Caddy. Tuy nhien, Caddy van huu ich de:
- Them security headers
- Xu ly CORS
- Load balancing trong tuong lai

### 6.1 Su dung Caddy voi Docker

Khi chay voi `--environment public`, Caddy se tu dong khoi dong:

```bash
python3 scripts/start_services.py --profile gpu-nvidia --environment public
```

### 6.2 Cau hinh Caddyfile

File `caddy/Caddyfile` da duoc cau hinh san. Chinh sua domain trong `.env`:

```bash
N8N_HOSTNAME=n8n.yourdomain.com
WEBUI_HOSTNAME=ai.yourdomain.com
SUPABASE_HOSTNAME=db.yourdomain.com
SEARXNG_HOSTNAME=search.yourdomain.com
LETSENCRYPT_EMAIL=admin@yourdomain.com
```

### 6.3 Cloudflare Tunnel -> Caddy -> Services

Neu muon dung Caddy lam trung gian:

```yaml
# ~/.cloudflared/config.yml (chi tro ve Caddy)
tunnel: <TUNNEL_ID>
credentials-file: /home/<user>/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: "*.yourdomain.com"
    service: http://localhost:443
  - service: http_status:404
```

Luc nay: `Cloudflare Tunnel -> Caddy (443) -> Docker Services`

---

## 7. Firewall (UFW)

### 7.1 Cau hinh co ban

```bash
# Bat UFW
sudo ufw enable

# Mac dinh: Chan tat ca incoming, cho phep outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Cho phep SSH (quan trong! Khong khoa minh ngoai server)
sudo ufw allow ssh

# Neu dung Caddy public
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Kiem tra rules
sudo ufw status verbose
```

### 7.2 Luu y ve Docker va UFW

> **CANH BAO**: Docker tu dong them iptables rules VA BYPASS ufw!
> Cac port published boi Docker (ports: "8080:8080") SE BI EXPOSE bat ke UFW.

Giai phap:
1. **Dung `expose` thay vi `ports`** trong docker-compose cho cac service noi bo
2. **Chi map ports cho Caddy** (80, 443) khi chay public
3. Hoac cau hinh Docker de khong bypass UFW:

```bash
# /etc/docker/daemon.json
{
  "iptables": false
}
# Sau do restart Docker va tu them iptables rules cho Docker network
```

---

## 8. Verification (BAT BUOC)

### Test 1: Kiem tra Tailscale VPN

**Thao tac**:
1. Tat Wi-Fi noi bo tren Laptop
2. Dung 4G/5G hoac mang khac
3. Bat Tailscale tren Client
4. Truy cap IP 100.x.x.x cua server

**Kiem tra**:
```bash
# SSH
ssh user@100.x.x.x

# Open WebUI
curl http://100.x.x.x:8080

# Hoac mo trinh duyet: http://100.x.x.x:8080
```

**Mong doi**: Truy cap thanh cong tat ca services qua IP VPN.

### Test 2: Kiem tra Zero Trust Authentication

**Thao tac**:
1. Mo trinh duyet an danh (Incognito) hoac thiet bi chua dang nhap
2. Truy cap `https://ai.yourdomain.com`

**Mong doi**:
- Cloudflare hien thi trang Login
- Yeu cau nhap Email
- Gui ma OTP qua Email
- Chi sau khi nhap OTP dung moi thay giao dien Open WebUI
- Email ngoai domain `@ten-cong-ty.com` bi tu choi

### Test 3: Kiem tra Remote Coding (VS Code)

**Thao tac**:
1. Mo VS Code tren Client
2. Cai extension "Remote - SSH"
3. Connect to: `user@ai-server` (MagicDNS) hoac `user@100.x.x.x`

**Kiem tra**:
```bash
# Trong VS Code Terminal (remote)
nvidia-smi          # Thay thong tin GPU
docker compose ps   # Thay tat ca services
ollama list         # Thay cac models da pull
```

**Mong doi**: Lam viec tu xa nhu dang ngoi truoc server.

### Test 4: Kiem tra bao mat

**Thao tac**:
```bash
# Tu mot may khong co Tailscale, thu truy cap truc tiep IP Public cua server
nmap -sT <public-ip-of-server>
```

**Mong doi**: Khong co port nao bi expose (tru 80/443 neu dung Caddy public).

---

## 9. Cai dat nhu Systemd Service (Auto-start)

### Tailscale

Tailscale tu dong chay nhu service sau khi cai dat. Verify:

```bash
sudo systemctl status tailscaled
sudo systemctl enable tailscaled
```

### Cloudflared

```bash
sudo systemctl status cloudflared
sudo systemctl enable cloudflared
```

### Docker Compose (Auto-start on boot)

Docker Compose services voi `restart: unless-stopped` se tu khoi dong khi Docker daemon start. Dam bao Docker tu start:

```bash
sudo systemctl enable docker
```

---

## 10. Common Issues & Fix

| Van de | Nguyen nhan | Giai phap |
|--------|------------|-----------|
| DNS chua co hieu luc | DNS Propagation | Doi 5-10 phut, dung `dig ai.yourdomain.com` de kiem tra |
| SSL/TLS Handshake Error | Cloudflare SSL setting | Dat SSL mode = "Full" hoac "Full (Strict)" trong Cloudflare Dashboard |
| Tailscale khong ping duoc | Firewall chan UDP | Cho phep UDP outbound, hoac Tailscale se dung DERP relay |
| Hostname khong resolve | MagicDNS chua bat | Bat MagicDNS tai https://login.tailscale.com/admin/dns |
| Tunnel Status: Inactive | cloudflared chua chay | `sudo systemctl restart cloudflared` |
| Zero Trust block tat ca | Policy sai | Kiem tra lai Email domain trong Access Policy |
| VS Code Remote timeout | Tailscale chua ket noi | Verify Tailscale status tren ca 2 thiet bi |

---

## 11. Ready Check (Gate sang Phase tiep theo)

- [ ] Tailscale da hoat dong tren ca Server va Client ca nhan
- [ ] Co the SSH vao server tu mang ngoai qua Tailscale
- [ ] Cloudflare Tunnel da ket noi on dinh (Status: Healthy)
- [ ] Co it nhat 1 subdomain duoc bao ve boi Zero Trust login
- [ ] Co the truy cap Open WebUI qua domain (sau khi xac thuc)
- [ ] VS Code Remote-SSH hoat dong qua Tailscale
- [ ] Khong co port nao bi expose truc tiep (ngoai 80/443 neu dung Caddy)
- [ ] Tat ca services tu dong khoi dong khi reboot server
