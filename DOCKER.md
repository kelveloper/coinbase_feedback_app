# Docker Guide for Advanced Trade Insight Engine

## 🐳 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git repository cloned locally

### Launch Dashboard (Production Mode)
```bash
# Build and start the dashboard
docker-compose up --build

# Access dashboard at: http://localhost:8501
```

### Development Mode
```bash
# Start development environment with live reload
docker-compose --profile dev up --build

# Access development dashboard at: http://localhost:8502
```

## 🚀 **Benefits for Collaborative Development**

### 1. **Consistent Environment**
- **Same Python version** (3.9) across all developer machines
- **Identical dependencies** locked in requirements.txt
- **No OS-specific issues** (works on macOS, Windows, Linux)

### 2. **Zero Setup Time**
- **New team members**: Just run `docker-compose up`
- **No manual installation** of Python, pip, dependencies
- **Immediate productivity** - start coding in minutes

### 3. **Isolated Development**
- **No conflicts** with other Python projects
- **Clean environment** every time
- **Easy cleanup** - just remove containers

### 4. **Production Parity**
- **Same container** runs in development and production
- **Eliminates** "works on my machine" problems
- **Predictable deployments**

## 📋 **Available Services**

### Main Dashboard Service
```bash
# Start dashboard (production mode)
docker-compose up insight-engine

# Access at: http://localhost:8501
```

### Development Service
```bash
# Start with live reload for development
docker-compose --profile dev up insight-engine-dev

# Access at: http://localhost:8502
# Files auto-reload when changed
```

### Pipeline Runner
```bash
# Run the main data processing pipeline
docker-compose --profile pipeline up pipeline-runner

# Processes CSV data and generates reports
```

### Test Runner
```bash
# Run the complete test suite
docker-compose --profile test up test-runner

# Runs all unit, integration, and e2e tests
```

## 🛠️ **Development Workflow**

### Daily Development
```bash
# 1. Pull latest changes
git pull origin main

# 2. Start development environment
docker-compose --profile dev up --build

# 3. Make code changes (auto-reload enabled)
# 4. Test changes at http://localhost:8502

# 5. Run tests
docker-compose --profile test up test-runner

# 6. Commit and push changes
git add .
git commit -m "Your changes"
git push origin feature-branch
```

### Team Collaboration
```bash
# When someone adds new dependencies:
# 1. Pull their changes
git pull origin main

# 2. Rebuild containers with new dependencies
docker-compose up --build

# No manual pip install needed!
```

## 🔧 **Common Commands**

### Container Management
```bash
# Start services
docker-compose up                    # Start default services
docker-compose up -d                 # Start in background
docker-compose up --build            # Rebuild and start

# Stop services
docker-compose down                  # Stop all services
docker-compose down -v               # Stop and remove volumes

# View logs
docker-compose logs                  # All service logs
docker-compose logs insight-engine   # Specific service logs
docker-compose logs -f               # Follow logs in real-time
```

### Development Commands
```bash
# Run pipeline manually
docker-compose --profile pipeline up pipeline-runner

# Run specific tests
docker-compose run test-runner python -m pytest tests/test_dashboard/ -v

# Access container shell
docker-compose exec insight-engine bash

# View running containers
docker-compose ps
```

### Cleanup Commands
```bash
# Remove containers and networks
docker-compose down

# Remove containers, networks, and images
docker-compose down --rmi all

# Remove everything including volumes
docker-compose down -v --rmi all

# Clean up Docker system
docker system prune -f
```

## 📊 **Service Details**

### Port Mapping
- **Dashboard (Production)**: http://localhost:8501
- **Dashboard (Development)**: http://localhost:8502

### Volume Mounts
- **Data**: `./csv_mock_data` → `/app/csv_mock_data` (read-only)
- **Output**: `./output` → `/app/output` (read-write)
- **Development**: `.` → `/app` (full project mount for dev)

### Environment Variables
- `PYTHONPATH=/app/src` - Python module path
- `STREAMLIT_SERVER_HEADLESS=true` - Headless mode
- `STREAMLIT_SERVER_PORT=8501` - Dashboard port

## 🚨 **Troubleshooting**

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :8501

# Kill the process or use different port
docker-compose up -p 8503:8501
```

#### Container Won't Start
```bash
# Check logs for errors
docker-compose logs insight-engine

# Rebuild from scratch
docker-compose down
docker-compose up --build --force-recreate
```

#### Permission Issues
```bash
# Fix output directory permissions
chmod 755 output/

# Or run with user permissions
docker-compose run --user $(id -u):$(id -g) insight-engine
```

#### Dependency Issues
```bash
# Rebuild with no cache
docker-compose build --no-cache

# Update requirements and rebuild
docker-compose up --build
```

## 🔒 **Security Best Practices**

### Data Protection
- CSV data mounted as read-only
- Output directory isolated
- No sensitive data in containers

### Network Security
- Services run on isolated Docker network
- Only necessary ports exposed
- Health checks enabled

### Container Security
- Non-root user in production
- Minimal base image (python:3.9-slim)
- Regular security updates

## 🚀 **Production Deployment**

### Build Production Image
```bash
# Build optimized production image
docker build -t coinbase-insight-engine:latest .

# Tag for registry
docker tag coinbase-insight-engine:latest your-registry/coinbase-insight-engine:v1.0
```

### Deploy to Production
```bash
# Push to registry
docker push your-registry/coinbase-insight-engine:v1.0

# Deploy with production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 **Performance Optimization**

### Build Optimization
- Multi-stage builds for smaller images
- Layer caching for faster builds
- .dockerignore to exclude unnecessary files

### Runtime Optimization
- Health checks for reliability
- Resource limits for stability
- Volume mounts for data persistence

## 🤝 **Team Guidelines**

### For New Team Members
1. Install Docker Desktop
2. Clone the repository
3. Run `docker-compose up --build`
4. Start developing immediately!

### For Existing Team Members
1. Always pull latest changes before starting
2. Rebuild containers when dependencies change
3. Use development profile for active coding
4. Run tests before committing

### Best Practices
- Use specific Docker tags, not `latest`
- Keep Dockerfile and docker-compose.yml in version control
- Document any Docker-specific setup in README
- Use .dockerignore to optimize build context