# Quick Start Guide (5 Minutes)

## Prerequisites
- Git
- GitHub CLI (`gh`) or HTTPS access
- Node.js 18+ (for JavaScript/TypeScript repos)
- Python 3.9+ (for Python repos)
- Docker & Docker Compose (for full stack)

---

## Option A: Local Development Setup (Fastest)

### Step 1: Clone the audit repo
```bash
git clone https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT.git
cd HEAVENZFIRE-ECOSYSTEM-AUDIT
```

### Step 2: Create environment file
```bash
cp .env.example .env
# Edit .env and add:
# GITHUB_TOKEN=your_github_token_here
# GITHUB_USER=HeavenzFire
```

### Step 3: Run orchestrator (will clone all 256 repos)
```bash
bash setup-orchestrator.sh --mode=development --workers=4
```

**What this does:**
- Clones all 256 repos to `./repos/`
- Installs dependencies in parallel
- Creates symlinks for common libraries
- Generates dependency graphs
- Runs initial health checks

**Time: ~10-15 minutes (first run)**

### Step 4: Start Neural Mesh Orchestrator
```bash
cd repos/Neural-Mesh-Orchestrator
npm install
npm run dev
```

**Access:** http://localhost:3000

---

## Option B: Docker Compose (Production-Ready)

### Step 1: Clone and enter
```bash
git clone https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT.git
cd HEAVENZFIRE-ECOSYSTEM-AUDIT
```

### Step 2: Start full stack
```bash
cp .env.prod.example .env
docker-compose -f deployment/docker-compose.prod.yml up -d
```

**What starts:**
- Neural Mesh Orchestrator (3000)
- PostgreSQL (5432)
- Redis (6379)
- Prometheus (9090)
- Grafana (3000, admin dashboard)
- ELK Stack (5601 for Kibana)
- All Tier S/A systems as microservices

**Time: ~3 minutes**

### Step 3: Verify deployment
```bash
# Check all services
docker-compose -f deployment/docker-compose.prod.yml ps

# View logs
docker-compose logs -f neural-mesh-orchestrator

# Health check
curl http://localhost:3000/api/health
```

---

## Option C: Kubernetes (Enterprise)

### Step 1: Verify cluster
```bash
kubectl cluster-info
kubectl get nodes
```

### Step 2: Add Helm repo
```bash
helm repo add heavenzfire https://charts.heavenzfire.io
helm repo update
```

### Step 3: Deploy
```bash
helm install heavenzfire heavenzfire/heavenzfire-ecosystem \
  --namespace heavenzfire \
  --create-namespace \
  --values deployment/helm/values.prod.yaml
```

**Time: ~5 minutes**

### Step 4: Access
```bash
# Get service endpoints
kubectl get ingress -n heavenzfire

# Port-forward to local
kubectl port-forward -n heavenzfire svc/neural-mesh-orchestrator 3000:3000
```

---

## Verify Installation

### Check Neural Mesh is running
```bash
curl -s http://localhost:3000/api/health | jq .
# Expected response:
# {
#   "status": "healthy",
#   "uptime_ms": 1234,
#   "neurons_online": 256,
#   "pathways_active": 42
# }
```

### List all neurons
```bash
curl -s http://localhost:3000/api/neurons | jq '.neurons | length'
# Should return: 256
```

### View domain breakdown
```bash
curl -s http://localhost:3000/api/neurons | jq '.neurons | group_by(.domain) | map({domain: .[0].domain, count: length})'
```

### Check metrics
```bash
curl -s http://localhost:3000/api/metrics/overview | jq .
```

---

## Access the Dashboards

| Dashboard | URL | User | Pass |
|-----------|-----|------|------|
| **Neural Mesh** | http://localhost:3000 | (public) | — |
| **Grafana** | http://localhost:3000/grafana | admin | admin |
| **Prometheus** | http://localhost:9090 | — | — |
| **Kibana** | http://localhost:5601 | elastic | changeme |
| **Jaeger** | http://localhost:16686 | — | — |

---

## Common Tasks

### Execute a Pathway
```bash
curl -X POST http://localhost:3000/api/pathways/execute \
  -H "Content-Type: application/json" \
  -d '{
    "pathway_id": "orchestrated-lattice-build",
    "payload": {
      "prompt": "Generate optimized React component",
      "context": { "framework": "react", "style": "tailwind" }
    }
  }'
```

### Register a New Neuron
```bash
curl -X POST http://localhost:3000/api/register \
  -H "Content-Type: application/json" \
  -d '@neuron-manifest.json'
```

### Monitor Failing Nodes
```bash
curl -s http://localhost:3000/api/neurons?status=offline | jq '.neurons[] | {id, domain, error}'
```

### View Audit Logs
```bash
curl -s http://localhost:3000/api/audit-logs?limit=50 | jq '.logs | reverse'
```

---

## Troubleshooting

### Port 3000 already in use
```bash
# Find what's using it
lsof -i :3000

# Kill and restart
kill -9 <PID>
npm run dev -- --port 3001
```

### Docker compose fails to start
```bash
# Check logs
docker-compose logs orchestrator

# Reset everything
docker-compose down -v
docker-compose up -d
```

### Neuron registration fails
```bash
# Check neuron manifest schema
jq -f deployment/schemas/neuron-manifest.schema.json neuron.json

# Verify dependencies are online
curl http://localhost:3000/api/neurons/<dependency-id>
```

### Kubernetes deployment stuck
```bash
# Check pod status
kubectl describe pod -n heavenzfire <pod-name>

# View recent events
kubectl get events -n heavenzfire --sort-by='.lastTimestamp'

# Tail logs
kubectl logs -f -n heavenzfire <pod-name>
```

---

## Next Steps

1. ✅ **System is running** (you should see dashboards at localhost:3000)
2. 📖 **Read full deployment guide**: `3-DEPLOYMENT_GUIDE.md`
3. 🔗 **Explore pathways**: `4-PATHWAY_LIBRARY.json`
4. 📊 **Review architecture**: `2-ARCHITECTURE_MAP.json`
5. 🚀 **Integrate your apps**: See API Reference in docs/

---

## Support

- **Docs**: [3-DEPLOYMENT_GUIDE.md](./3-DEPLOYMENT_GUIDE.md)
- **Issues**: https://github.com/HeavenzFire/Neural-Mesh-Orchestrator/issues
- **Discussions**: https://github.com/HeavenzFire/HEAVENZFIRE-ECOSYSTEM-AUDIT/discussions

---

**Happy orchestrating!** 🚀
