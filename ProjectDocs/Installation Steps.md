
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

👉 Do you want me to **scaffold a minimal working repo** (dummy gRPC sender/receiver, Flask UI with onboarding page, Nginx + TLS, CouchDB connection) so you can run `docker-compose up` and see the skeleton working? That way you’d have a running baseline and can incrementally add logic.