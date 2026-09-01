# Docker Image Version Control

## 🎯 How to Use Versioning

### **Method 1: Environment Variable (Recommended)**

Create a `.env` file:
```bash
VERSION=v1.0
```

Then build:
```bash
docker compose build
```

This creates TWO tags:
- `trip-planner-api:v1.0` (your version)
- `trip-planner-api:latest` (always latest)

---

### **Method 2: Command Line**

```bash
VERSION=v1.0 docker compose build
```

---

### **Method 3: Export (Session-wide)**

```bash
export VERSION=v1.0
docker compose build
```

---

## 📝 Version Naming Strategies

### **Semantic Versioning:**
```bash
VERSION=v1.0.0  # Major.Minor.Patch
VERSION=v1.1.0
VERSION=v2.0.0
```

### **Date-based:**
```bash
VERSION=2024-01-15
VERSION=2024-01-16
```

### **Git-based:**
```bash
VERSION=$(git rev-parse --short HEAD)  # e.g., abc123d
VERSION=v1.0-$(git rev-parse --short HEAD)  # e.g., v1.0-abc123d
```

### **Environment-based:**
```bash
VERSION=dev
VERSION=staging
VERSION=prod
```

---

## 🔄 Typical Workflow

### **Development:**
```bash
# No VERSION set = uses 'latest'
docker compose build
docker compose up
```

### **Creating a Release:**
```bash
# Tag with version
VERSION=v1.0 docker compose build

# Verify images
docker images | grep trip-planner

# Push to registry (later)
docker push trip-planner-api:v1.0
```

### **Rollback to Previous Version:**
```bash
# Use specific version
VERSION=v0.9 docker compose up
```

---

## 🎓 What You Get

### **Before (no versioning):**
```
trip-planner-api-api:latest
```

### **After (with versioning):**
```
trip-planner-api:latest
trip-planner-api:v1.0
trip-planner-api:v1.1
trip-planner-api:v2.0
```

**All tracked and manageable!** ✅

---

## 🚀 For Kubernetes/Production

When you move to K8s, you'll reference specific versions:

```yaml
# deployment.yaml
spec:
  containers:
  - name: api
    image: myregistry/trip-planner-api:v1.0  # Pinned version!
```

**Never use `latest` in production!**

---

## 📊 Check Your Images

```bash
# See all versions
docker images | grep trip-planner-api

# Clean up old versions
docker image prune -a
```
