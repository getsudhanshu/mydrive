
Great 👍 — this is now a well-scoped project with clear services. I’ll walk you through **step by step** how to set up your development and deployment workflow with `uv` + Docker Compose, keeping things cross-platform (Ubuntu + Windows).

---

# **Step 1: `uv` Setup (Python deps & virtualenvs)**

[`uv`](https://github.com/astral-sh/uv) will be your dependency + venv manager (instead of `pip`/`poetry`).

### Install uv

**Ubuntu (Linux):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Initialize your repo

```bash
mkdir mydrive
cd mydrive
git init
uv init
```

This creates:

- `pyproject.toml` (dependencies live here)
    
- `.venv/` (virtual environment)
    

### Add dependencies

```bash
uv add grpcio grpcio-tools flask flask-wtf flask-login
uv add couchdb requests cryptography
```

You’ll have:

- **gRPC** → File sender & receiver
    
- **Flask** → UI/UX service
    
- **couchdb** → Python client for CouchDB
    
- **cryptography** → encryption for file chunks
    

---

# **Step 2: Repo Folder Structure**

Keep **one repo** with clear service separation + shared code:

```
mydrive/
├── services/
│   ├── file_sender/
│   │   ├── main.py
│   │   ├── proto/          # protobufs for gRPC
│   ├── file_receiver/
│   │   └── main.py
│   ├── uiux/
│   │   ├── app.py          # Flask app
│   │   └── templates/      # onboarding, passphrase rotation, file tree
│   ├── shared_lib/         # single version of truth for shared code
│   │   ├── crypto_utils.py
│   │   ├── db_utils.py
│   │   └── __init__.py
├── nginx/
│   └── nginx.conf
├── docker/
│   ├── Dockerfile.base
│   ├── Dockerfile.sender
│   ├── Dockerfile.receiver
│   ├── Dockerfile.uiux
│   └── Dockerfile.nginx
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

---

# **Step 3: Docker Setup**

You want **one base Python image** (so deps aren’t duplicated), then small service images.

### Base Dockerfile

`docker/Dockerfile.base`

```dockerfile
FROM python:3.12-slim AS base

RUN pip install uv

WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN uv sync --no-dev
```

### File Sender

`docker/Dockerfile.sender`

```dockerfile
FROM base AS sender
WORKDIR /app
COPY services/file_sender /app/file_sender
COPY services/shared_lib /app/shared_lib
CMD ["python", "-m", "file_sender.main"]
```

Repeat for `receiver` and `uiux`.

### Nginx

`docker/Dockerfile.nginx`

```dockerfile
FROM nginx:alpine
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/certs /etc/nginx/certs   # TLS certs
```

---

# **Step 4: docker-compose.yml**

This ties all services together.

```yaml
version: "3.9"
services:
  file_sender:
    build: { context: ., dockerfile: docker/Dockerfile.sender }
    networks: [p2p_net]

  file_receiver:
    build: { context: ., dockerfile: docker/Dockerfile.receiver }
    networks: [p2p_net]

  uiux:
    build: { context: ., dockerfile: docker/Dockerfile.uiux }
    ports:
      - "8080:8080"    # Browser UI
    networks: [p2p_net]

  nginx:
    build: { context: ., dockerfile: docker/Dockerfile.nginx }
    ports:
      - "443:443"
    depends_on:
      - file_sender
      - file_receiver
      - couchdb
    networks: [p2p_net]

  couchdb:
    image: couchdb:3
    environment:
      - COUCHDB_USER=admin
      - COUCHDB_PASSWORD=secret
    volumes:
      - couchdb_data:/opt/couchdb/data
    ports:
      - "5984:5984"
    networks: [p2p_net]

networks:
  p2p_net:

volumes:
  couchdb_data:
```

---

# **Step 5: Nginx Setup**

Peers talk via **Nginx TLS termination**.

### nginx/nginx.conf

```nginx
events {}

http {
    upstream file_sender {
        server file_sender:50051;  # gRPC service
    }
    upstream file_receiver {
        server file_receiver:50052;
    }
    upstream couchdb {
        server couchdb:5984;
    }
    upstream uiux {
        server uiux:8080;
    }

    server {
        listen 443 ssl http2;
        server_name mydrive.local;

        ssl_certificate     /etc/nginx/certs/mydrive.crt;
        ssl_certificate_key /etc/nginx/certs/mydrive.key;

        location /sender {
            grpc_pass grpc://file_sender;
        }
        location /receiver {
            grpc_pass grpc://file_receiver;
        }
        location /couchdb {
            proxy_pass http://couchdb;
        }
        location /ui {
            proxy_pass http://uiux;
        }
    }
}
```

---

# **Step 6: TLS Keys Between Peers**

Instead of SSH, use TLS certs (simpler with Nginx & gRPC).

### Create CA + certs (on Ubuntu, works on WSL too):

```bash
mkdir nginx/certs
cd nginx/certs

# Create CA
openssl genrsa -out mydriveCA.key 4096
openssl req -x509 -new -nodes -key mydriveCA.key -sha256 -days 365 -out mydriveCA.crt -subj "/CN=mydriveCA"

# Create server key + CSR
openssl genrsa -out mydrive.key 2048
openssl req -new -key mydrive.key -out mydrive.csr -subj "/CN=mydrive.local"

# Sign with CA
openssl x509 -req -in mydrive.csr -CA mydriveCA.crt -CAkey mydriveCA.key -CAcreateserial -out mydrive.crt -days 365 -sha256
```

Distribute:

- `mydriveCA.crt` → trusted by all peers
    
- `mydrive.crt` + `mydrive.key` → mounted in Nginx container
    

---

# **Step 7: Cross-Platform Deployment (Ubuntu + Windows)**

✅ With Docker + Docker Compose, the setup is **identical** on Ubuntu and Windows.

- On **Ubuntu**: install Docker CE + docker-compose-plugin.
    
- On **Windows**: install Docker Desktop (with WSL2 backend).
    

Your repo + `docker-compose.yml` will run unchanged.

---

# **Step 8: Service Interactions**

- **File Sender** ↔ **File Receiver**:  
    gRPC calls via `nginx:443` (with TLS termination).
    
- **UI/UX** ↔ **CouchDB**:  
    Flask calls CouchDB REST API.
    
- **UI/UX** ↔ **File Receiver**:  
    User selects files → UI service sends request to File Receiver to fetch chunks.
    
- **CouchDB**:  
    Master–master replication across peers via `_replicator` DB.
    

---

✅ At this point you’ll have:

- `uv` dependency mgmt
    
- Shared library (`services/shared_lib/`)
    
- Docker images for each service
    
- Nginx for TLS + routing
    
- CouchDB replicated across peers
    
- Flask UI for onboarding / file tree
    

---

Perfect 👍 — let’s wire these certs into **Nginx** so it can terminate TLS for both:

- **gRPC** traffic (between `file-sender` and `file-receiver`)
    
- **HTTP (Flask + UI/UX)** traffic
    

---

## 1. File locations after cert generation

From the earlier OpenSSL steps, inside your repo you have:

```
nginx/
 ├─ certs/
 │   ├─ mydriveCA.crt       # Root CA (trusted by peers/browsers)
 │   ├─ mydriveCA.key       # CA private key (keep secret!)
 │   ├─ mydriveCA.srl       # Serial file (auto-created by openssl)
 │   ├─ mydrive.crt         # Server TLS cert (signed by CA)
 │   ├─ mydrive.key         # Server private key
 └─ nginx.conf              # Nginx config (we’ll write now)
```

---

## 2. Example Nginx Config for MyDrive (`nginx/nginx.conf`)

```nginx
events { }

http {
    # Default log format
    access_log /var/log/nginx/access.log;
    error_log  /var/log/nginx/error.log;

    # === TLS Server Block ===
    server {
        listen 443 ssl http2;
        server_name mydrive.local;

        # TLS cert + private key (signed by your CA)
        ssl_certificate     /etc/nginx/certs/mydrive.crt;
        ssl_certificate_key /etc/nginx/certs/mydrive.key;

        # Modern TLS config
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        # === Route for gRPC to File Sender ===
        location /file-sender {
            grpc_pass grpc://file-sender:50051;
        }

        # === Route for gRPC to File Receiver ===
        location /file-receiver {
            grpc_pass grpc://file-receiver:50052;
        }

        # === Route for CouchDB replication ===
        location /couchdb/ {
            proxy_pass http://couchdb:5984/;
        }

        # === Route for UI/UX (Flask via Gunicorn) ===
        location /ui/ {
            proxy_pass http://uiux:8080/;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $remote_addr;
        }
    }
}
```

---

## 3. How this works

1. **TLS termination**
    
    - Clients (peers, browsers) connect to `https://mydrive.local` on port 443.
        
    - Nginx uses `mydrive.crt` + `mydrive.key` to establish an encrypted channel.
        
    - Peers/browsers must **trust** `mydriveCA.crt` (import into system/browser trust store).
        
2. **Routing**
    
    - Requests with prefix `/file-sender` → proxied to `file-sender` container (gRPC service on port 50051).
        
    - Requests with prefix `/file-receiver` → proxied to `file-receiver` container (gRPC service on port 50052).
        
    - Requests with prefix `/couchdb/` → proxied to CouchDB container on `5984`.
        
    - Requests with prefix `/ui/` → proxied to Flask (Gunicorn) container on `8080`.
        
3. **Container Networking**
    
    - Inside `docker-compose.yml`, all services (`nginx`, `file-sender`, `file-receiver`, `couchdb`, `uiux`) run on the same Docker network.
        
    - That’s why you can say `grpc://file-sender:50051` instead of IP.
        

---

## 4. Example docker-compose snippet for Nginx

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: mydrive-nginx
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - file-sender
      - file-receiver
      - couchdb
      - uiux
```

---

## 5. Peers & trust

- Each peer will generate its own **CA** + **server cert**, OR you can share one CA (`mydriveCA.crt`) across all peers and just sign each peer’s cert with it.
    
- Every peer must **import `mydriveCA.crt` into its trust store** so TLS handshakes succeed.
    
    - On Linux: copy `mydriveCA.crt` → `/usr/local/share/ca-certificates/` and run `update-ca-certificates`.
        
    - On Windows: import into "Trusted Root Certification Authorities".
        
    - On browsers: import manually if testing UI.
        

---

✅ At this point:

- All peers talk **mutually authenticated, encrypted gRPC/HTTP** through Nginx.
    
- UI (Flask+Gunicorn) sits behind Nginx.
    
- CouchDB replication also tunnels through Nginx → clean TLS + routing setup.
    

---

Would you like me to **extend this config for mutual TLS (mTLS)**, so that peers must present _their own certs_ back to Nginx (not just server-side TLS)? That would prevent “unauthorized” peers from joining the cluster.

