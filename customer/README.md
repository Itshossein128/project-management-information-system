# IPCAS — Customer PC deployment (Docker)

Run IPCAS on a customer PC without cloud hosting. Updates are one double-click after you push to Git.

## What you need on the PC

| Requirement | Notes |
|-------------|--------|
| **Docker Desktop** | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — Windows or Mac |
| **Git** | [git-scm.com](https://git-scm.com/) — required for updates |
| **RAM** | 8 GB minimum, 16 GB recommended |
| **Disk** | ~10 GB free |

## One-time setup

### 1. Clone the repository

```bash
git clone <your-repository-url> building-management
cd building-management
```

For a **private** repository, set up access once:

- **HTTPS:** Git Credential Manager (installed with Git for Windows) will prompt for username + personal access token.
- **SSH:** Add the customer’s SSH key to the repository deploy keys.

### 2. Install and start

| OS | Action |
|----|--------|
| **Windows** | Double-click `customer\install.bat` |
| **Mac / Linux** | Run `bash customer/install.sh` |

First start builds Docker images and may take **5–15 minutes**. The browser opens to:

**http://localhost:8080**

### 3. Demo login

| Field | Value |
|-------|--------|
| Phone | `+10000000001` |
| Password | `devpass123` |

## Daily use

| Action | Windows | Mac / Linux |
|--------|---------|-------------|
| **Start** | `customer\start.bat` | `bash customer/start.sh` |
| **Stop** | `customer\stop.bat` | `bash customer/stop.sh` |
| **Update** (after you push code) | `customer\update.bat` | `bash customer/update.sh` |

**Tip:** Pin shortcuts to the desktop for `start.bat` and `update.bat`.

### What “Update” does

1. `git pull` from your repository (branch in `customer/ipcas.config`, default `main`)
2. Rebuild Docker images if code changed
3. Restart the stack
4. Open the browser when ready

No manual `docker compose` commands are required.

## Optional configuration

Copy `customer/ipcas.config.example` to `customer/ipcas.config` and edit:

```bash
GIT_BRANCH=main          # branch to pull on update
APP_URL=http://localhost:8080
```

On first run, `.env` is created automatically from `.env.customer.example`.

## Troubleshooting

**“Docker is not running”**  
Open Docker Desktop and wait until it shows **Running**, then try again.

**Update fails with authentication**  
Re-enter Git credentials, or switch the clone to SSH.

**Port 8080 already in use**  
Change `TRAEFIK_HTTP_PORT` in `.env` and `APP_URL` in `customer/ipcas.config`, then restart.

**View logs**

```bash
bash customer/scripts/compose.sh logs -f
```

On Windows: `customer\scripts\compose.bat logs -f`

**Reset all data** (fresh demo)

```bash
bash customer/scripts/compose.sh down -v
```

Then run install/start again.

## For developers (distributing to customers)

1. Push releases to the branch customers track (usually `main`).
2. Give customers: repository URL + this folder’s instructions.
3. Optionally send a one-page PDF with screenshots of `install.bat` → browser login.

Technical stack started by these scripts:

- PostgreSQL, RabbitMQ, MinIO, Django API, worker, React web, Traefik gateway
- Demo data seeded automatically (`SEED_DEMO_DATA=true` in `docker-compose.customer.yml`)
