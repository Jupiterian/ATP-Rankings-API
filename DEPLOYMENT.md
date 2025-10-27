# Deployment Guide for ATP Rankings FastAPI Application

This guide covers how to deploy your ATP Rankings FastAPI application to various platforms.

## Table of Contents
1. [Pushing to GitHub](#pushing-to-github)
2. [Deploying to Render](#deploying-to-render)
3. [Deploying to Railway](#deploying-to-railway)
4. [Deploying to Fly.io](#deploying-to-flyio)
5. [Deploying to Heroku](#deploying-to-heroku)

---

## Pushing to GitHub

### First Time Setup

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   ```

2. **Add all files**:
   ```bash
   git add .
   ```

3. **Commit your changes**:
   ```bash
   git commit -m "Add FastAPI application with ATP rankings data"
   ```

4. **Create a new repository on GitHub**:
   - Go to [github.com](https://github.com)
   - Click the "+" icon in the top right
   - Select "New repository"
   - Name it (e.g., "ATP-Rankings-Data-Visualization")
   - Don't initialize with README (you already have one)
   - Click "Create repository"

5. **Connect your local repo to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ATP-Rankings-Data-Visualization.git
   git branch -M main
   git push -u origin main
   ```

### Updating Your Repository

After making changes:
```bash
git add .
git commit -m "Description of your changes"
git push
```

---

## Deploying to Render

Render is a free and easy platform for deploying Python applications.

### Steps:

1. **Sign up at [render.com](https://render.com)**

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**

4. **Configure the service**:
   - **Name**: atp-rankings (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. **Click "Create Web Service"**

6. **Your app will be live at**: `https://your-app-name.onrender.com`

### Notes:
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Database file (`rankings.db`) must be committed to your repo

---

## Deploying to Railway

Railway offers a simple deployment with automatic builds from GitHub.

### Steps:

1. **Sign up at [railway.app](https://railway.app)**

2. **Click "New Project"**

3. **Select "Deploy from GitHub repo"**

4. **Connect your GitHub account and select your repository**

5. **Railway will auto-detect Python and deploy**

6. **Add environment variables** (if needed):
   - Go to your project settings
   - Add any environment variables

7. **Generate a domain**:
   - Go to Settings → Networking
   - Click "Generate Domain"

8. **Your app will be live at**: `https://your-app.up.railway.app`

### Notes:
- Railway provides $5 free credits per month
- Automatic deployments on every git push
- Includes persistent storage options

---

## Deploying to Fly.io

Fly.io is great for global deployment with edge locations.

### Steps:

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up and login**:
   ```bash
   fly auth signup
   # or
   fly auth login
   ```

3. **Create a `fly.toml` file** in your project root:
   ```toml
   app = "atp-rankings"
   
   [build]
   
   [env]
     PORT = "8000"
   
   [http_service]
     internal_port = 8000
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0
   
   [[vm]]
     cpu_kind = "shared"
     cpus = 1
     memory_mb = 256
   ```

4. **Create a `Dockerfile`**:
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

5. **Launch your app**:
   ```bash
   fly launch
   ```

6. **Deploy**:
   ```bash
   fly deploy
   ```

7. **Your app will be live at**: `https://atp-rankings.fly.dev`

### Notes:
- Free tier includes 3 shared-cpu VMs
- Apps scale to zero when not in use
- Global deployment across multiple regions

---

## Deploying to Heroku

Heroku is a traditional platform-as-a-service (PaaS).

### Steps:

1. **Install Heroku CLI**:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a Heroku app**:
   ```bash
   heroku create atp-rankings
   ```

4. **Ensure you have these files** (already created):
   - `Procfile`
   - `requirements.txt`
   - `runtime.txt`

5. **Deploy to Heroku**:
   ```bash
   git push heroku main
   ```

6. **Open your app**:
   ```bash
   heroku open
   ```

7. **View logs** (if needed):
   ```bash
   heroku logs --tail
   ```

### Notes:
- Heroku no longer offers a free tier (paid plans start at $7/month)
- Supports automatic deployments from GitHub
- Includes built-in CI/CD

---

## Important Considerations

### Database File
Your `rankings.db` file must be included in your git repository for deployment to work. The `.gitignore` file currently allows this (the line `# rankings.db` is commented out).

To ensure the database is tracked:
```bash
git add rankings.db
git commit -m "Add rankings database"
git push
```

### Environment Variables
For production, you may want to add environment variables:

Create a `.env` file locally (already in `.gitignore`):
```env
DATABASE_URL=rankings.db
PORT=8000
```

Update `main.py` to use environment variables:
```python
import os
DB_PATH = os.getenv("DATABASE_URL", "rankings.db")
```

### Static Files Optimization
If you want to add CSS/JS files, create a `static` folder and update `main.py`:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### HTTPS and Domain
Most platforms provide:
- Free HTTPS certificates
- Custom domain support
- Automatic renewals

---

## Troubleshooting

### Port Issues
Make sure your app reads the PORT from environment:
```python
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Database Not Found
Ensure `rankings.db` is:
1. Committed to git
2. In the root directory
3. Readable by the application

### Build Failures
Check:
1. `requirements.txt` has all dependencies
2. Python version matches `runtime.txt`
3. Build logs for specific errors

---

## Recommended Platform

For beginners: **Render.com**
- Free tier
- Simple setup
- Automatic HTTPS
- GitHub integration

For advanced users: **Fly.io**
- Better performance
- Global deployment
- More control
- Free tier available

---

## Next Steps

1. Choose a platform
2. Follow the platform-specific steps above
3. Deploy your application
4. Share your live URL!

Need help? Check the platform's documentation or community forums.
