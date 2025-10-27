# Quick Git & Deployment Commands

## Initial Setup (First Time Only)

### 1. Check Git Status
```bash
git status
```

### 2. Stage All Files
```bash
git add .
```

### 3. Commit Changes
```bash
git commit -m "Add FastAPI web application and deployment files"
```

### 4. Connect to GitHub
First, create a new repository on GitHub, then:
```bash
# If this is a new repo (not already on GitHub)
git remote add origin https://github.com/Jupiterian/ATP-Rankings-Data-Visualization.git

# If the repo already exists on GitHub, update the remote
git remote set-url origin https://github.com/Jupiterian/ATP-Rankings-Data-Visualization.git
```

### 5. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

---

## Regular Updates (After Making Changes)

```bash
# Check what changed
git status

# Add all changes
git add .

# Commit with a message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

---

## Common Scenarios

### View Current Remote
```bash
git remote -v
```

### View Commit History
```bash
git log --oneline
```

### Undo Uncommitted Changes
```bash
# Undo changes to a specific file
git checkout -- filename.py

# Undo all uncommitted changes
git reset --hard
```

### Create a New Branch
```bash
git checkout -b feature-name
git push -u origin feature-name
```

---

## Files Created for Deployment

✅ `.gitignore` - Excludes unnecessary files from git  
✅ `Procfile` - Tells hosting platforms how to run your app  
✅ `runtime.txt` - Specifies Python version  
✅ `DEPLOYMENT.md` - Detailed deployment instructions  
✅ `README.md` - Updated with web app info  

---

## Next Steps

1. **Verify files are ready**:
   ```bash
   git status
   ```

2. **Check if you have a GitHub repo already**:
   ```bash
   git remote -v
   ```

3. **If you see a remote URL**: Just commit and push
   ```bash
   git add .
   git commit -m "Add FastAPI application"
   git push
   ```

4. **If no remote**: Follow "Initial Setup" above

5. **Deploy**: Choose a platform from DEPLOYMENT.md and follow the instructions

---

## Recommended Deployment Path

1. ✅ Push to GitHub (preserves your code)
2. ✅ Deploy to Render.com (easiest free hosting)
3. ✅ Share your live URL!

See `DEPLOYMENT.md` for detailed platform-specific instructions.
