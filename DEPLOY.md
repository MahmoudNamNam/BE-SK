# Deploying the Skin Tone Classifier API

## Environment variable

Set **`ROBOFLOW_API_KEY`** so the `/classify` endpoint can run eye detection (darkcircle/eyebag).  
Skin-tone classification works without it; eyes fields are omitted if the key is missing.

---

## Free deployment options

All of these have a free tier. Pick one and add `ROBOFLOW_API_KEY` as an environment variable.

| Platform    | Free tier notes                          | Deploy from              |
|------------|-------------------------------------------|--------------------------|
| **Railway** | $5 credit/month (enough for small API)   | GitHub or Docker image   |
| **Render**  | Free web service (spins down after ~15 min idle) | GitHub (Docker)  |
| **Fly.io**  | 3 shared-cpu VMs, 3GB storage            | GitHub or `fly deploy`   |
| **Koyeb**   | 1 free service                           | GitHub or Docker image   |
| **Google Cloud Run** | 2M requests/month free              | Container image (e.g. Docker Hub) |

**Easiest free paths:**

1. **Render (free)**  
   - [render.com](https://render.com) → Sign up (GitHub).  
   - New → **Web Service** → Connect this repo.  
   - Environment: **Docker**.  
   - Add variable: `ROBOFLOW_API_KEY`.  
   - Deploy. You get a URL; the service sleeps when idle and wakes on request (cold start ~30–60 s).

2. **Fly.io (free)**  
   - Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/), then in the project root:
   ```bash
   fly launch
   fly secrets set ROBOFLOW_API_KEY=your_key
   fly deploy
   ```
   - Free tier: small VMs; you get a URL like `https://your-app.fly.dev`.

3. **Railway (free $5 credit)**  
   - [railway.app](https://railway.app) → Login with GitHub.  
   - New Project → **Deploy from GitHub** (connect this repo) or **Deploy from Docker image** → `mahmoudhamed22/beauty-api:latest`.  
   - Variables → add `ROBOFLOW_API_KEY`.  
   - Settings → Generate domain. Credit covers light usage.

4. **Google Cloud Run (free tier)**  
   - Push image to Docker Hub (or Google Artifact Registry).  
   - [console.cloud.google.com/run](https://console.cloud.google.com/run) → Create Service → choose your image → set env `ROBOFLOW_API_KEY` → Deploy.  
   - Free: 2 million requests/month; service scales to zero when idle.

---

## After building an image

**1. Build the image**

```bash
docker build -t beauty-api .
```

**2. Run locally**

```bash
docker run -p 8000:8000 -e ROBOFLOW_API_KEY=your_key beauty-api
```

Open **http://localhost:8000/docs**.

**3. Push to a registry (to deploy elsewhere)**

Tag and push to Docker Hub:

```bash
docker tag beauty-api mahmoudhamed22/beauty-api:latest
docker login
docker push mahmoudhamed22/beauty-api:latest
```

Or push to **GitHub Container Registry** (ghcr.io):

```bash
docker tag beauty-api ghcr.io/your-username/beauty-api:latest
docker login ghcr.io   # use a GitHub Personal Access Token
docker push ghcr.io/your-username/beauty-api:latest
```

**4. Deploy the image**

- **Railway:** New Project → Deploy from GitHub, or use “Deploy from Docker image” and paste your image URL (e.g. `mahmoudhamed22/beauty-api:latest`). Add env var `ROBOFLOW_API_KEY`.
- **Render:** New → Web Service → use “Docker” and connect your repo (Render builds from source), or use a “Private Service” and specify your image URL if supported.
- **Fly.io:** After `fly launch`, set `ROBOFLOW_API_KEY` with `fly secrets set`, then `fly deploy` (builds from Dockerfile). To use a pre-built image, configure your `fly.toml` with the image and run `fly deploy`.
- **Any VPS:** `docker pull mahmoudhamed22/beauty-api:latest` then `docker run -p 8000:8000 -e ROBOFLOW_API_KEY=your_key -d mahmoudhamed22/beauty-api:latest` (add `-d` to run in background).

---

## 1. Docker (local or any host)

**Build and run:**

```bash
docker build -t skin-tone-api .
docker run -p 8000:8000 -e ROBOFLOW_API_KEY=your_key skin-tone-api
```

API: **http://localhost:8000** — docs at **http://localhost:8000/docs**.

**Optional:** Use a `.env` file and pass it:

```bash
docker run -p 8000:8000 --env-file .env skin-tone-api
```

---

## 2. Railway

1. Push the repo to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub** → select the repo.
3. **Variables:** add `ROBOFLOW_API_KEY` = your key.
4. **Settings:**  
   - **Root Directory:** leave empty.  
   - **Build Command:** `docker build -t app .` (or leave default if it uses Dockerfile).  
   - **Start Command:** leave default if Railway detects the Dockerfile.
5. Deploy. Railway will assign a URL (e.g. `https://your-app.up.railway.app`).

---

## 3. Render

1. Push the repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Web Service** → connect the repo.
3. **Environment:** Docker.
4. **Environment Variables:** add `ROBOFLOW_API_KEY` = your key.
5. **Deploy.** Render will build from the Dockerfile and give a URL.

---

## 4. Fly.io

```bash
# Install flyctl, then:
fly launch   # follow prompts, choose region
fly secrets set ROBOFLOW_API_KEY=your_key
fly deploy
```

Fly will use the Dockerfile. Your app will be at `https://your-app.fly.dev`.

---

## 5. Run without Docker (VPS or your machine)

```bash
# In the project root
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
export ROBOFLOW_API_KEY=your_key
uvicorn main:app --host 0.0.0.0 --port 8000
```

Use a process manager (systemd, supervisor, or a reverse proxy) to keep it running.

---

## Port

The Dockerfile uses **port 8000** by default. Platforms that set **`PORT`** (e.g. Render, Railway) are supported: the container starts uvicorn with that port.
