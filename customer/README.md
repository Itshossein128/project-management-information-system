# IPCAS — Customer PC deployment (Docker)

Run IPCAS on a customer PC without cloud hosting. **Double-click** launcher scripts — no terminal commands needed on Windows.

## What you need on the PC

| Requirement | Notes |
|-------------|--------|
| **Docker Desktop** | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — Windows or Mac. On Windows, accept WSL2 when prompted during install. |
| **Git** | Only needed if you use **Update** to pull new code. Not required for a one-time demo. |
| **RAM** | 8 GB minimum, 16 GB recommended |
| **Disk** | ~10 GB free |

## Presenting to a non-technical customer (recommended)

Do this **before** the meeting on your own machine (or the demo laptop) while online:

| OS | Pre-build images |
|----|------------------|
| **Windows** | Double-click `customer\prepare.bat` |
| **Mac / Linux** | Run `bash customer/prepare.sh` |

On **demo day**, the customer only needs:

1. **Docker Desktop** installed and running (whale icon in the tray).
2. Copy the project folder (USB, zip, or Git clone).
3. Double-click **`customer\start.bat`** (Windows) or run **`bash customer/start.sh`** (Mac/Linux).

The browser opens to **http://localhost:8080**. Demo login: `+10000000001` / `devpass123`.

Pin a desktop shortcut to `start.bat` so they can launch IPCAS with one click later.

**First install** on a PC without pre-built images: use `install.bat` / `install.sh` instead (5–20 minutes, needs internet).

## One-time setup (Git clone path)

### 1. Clone the repository

```bash
git clone <your-repository-url> building-management
cd building-management
```

For a **private** repository, set up access once:

- **HTTPS:** Git Credential Manager (installed with Git for Windows) will prompt for username + personal access token.
- **SSH:** Add the customer's SSH key to the repository deploy keys.

### 2. Install and start

| OS | Action |
|----|--------|
| **Windows** | Double-click `customer\install.bat` |
| **Mac / Linux** | Run `bash customer/install.sh` |

First start builds Docker images and may take **5–20 minutes**. The browser opens to:

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

### What "Update" does

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

**"Docker is not installed"**  
Install Docker Desktop, restart the PC if prompted, then try again.

**"Docker is not running"**  
Open Docker Desktop and wait until it shows **Running**, then try again.

**Update fails with authentication**  
Re-enter Git credentials, or switch the clone to SSH.

**Port 8080 already in use**  
Change `TRAEFIK_HTTP_PORT` in `.env` and `APP_URL` / `HEALTH_URL` in `customer/ipcas.config`, then restart.

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

1. Run `prepare.bat` / `prepare.sh` before handing off the folder or USB stick.
2. Push releases to the branch customers track (usually `main`) if they use Update.
3. Give customers: project folder + "open Docker Desktop, then double-click start.bat".
4. Optionally send a one-page PDF with screenshots of Docker Desktop → `start.bat` → browser login.

Technical stack started by these scripts:

- PostgreSQL, RabbitMQ, MinIO, Django API, worker, React web, Traefik gateway
- Demo data seeded automatically (`SEED_DEMO_DATA=true` in `docker-compose.customer.yml`)
