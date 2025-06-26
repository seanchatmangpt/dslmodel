# Installation Guide

## System Requirements

### Minimum Requirements
- **Python**: 3.12 or higher
- **Memory**: 512MB RAM
- **Storage**: 100MB disk space
- **Network**: Internet access for package downloads

### Recommended Requirements
- **Python**: 3.12+
- **Memory**: 2GB RAM (for multiple agents)
- **Storage**: 1GB disk space (with OpenTelemetry traces)
- **CPU**: 2+ cores for concurrent agent processing

### Supported Platforms
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **macOS**: 12.0+ (Monterey)
- **Windows**: Windows 10+ with WSL2 recommended

## Installation Methods

### Option 1: PyPI Installation (Recommended)

**Basic Installation**:
```bash
pip install dslmodel
```

**With OpenTelemetry Support**:
```bash
pip install dslmodel[otel]
```

**With All Optional Dependencies**:
```bash
pip install dslmodel[otel,dev,test]
```

### Option 2: Poetry Installation

**Install Poetry** (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Clone and Install**:
```bash
git clone https://github.com/seanchatmangpt/dslmodel.git
cd dslmodel
poetry install --extras otel
```

**Activate Environment**:
```bash
poetry shell
```

### Option 3: Development Installation

**For Contributors**:
```bash
git clone https://github.com/seanchatmangpt/dslmodel.git
cd dslmodel
poetry install --extras "otel dev test"
poetry run pre-commit install
```

**For Local Development**:
```bash
pip install -e .[otel,dev,test]
```

## Docker Installation

### Pre-built Images

**Pull from Docker Hub**:
```bash
docker pull dslmodel/swarm:latest
```

**Run SwarmAgent**:
```bash
docker run -it dslmodel/swarm:latest dsl swarm status
```

### Build from Source

**Dockerfile**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install .[otel]

ENTRYPOINT ["dsl"]
CMD ["swarm", "--help"]
```

**Build and Run**:
```bash
docker build -t dslmodel-local .
docker run -it dslmodel-local swarm status
```

## Environment Setup

### Basic Configuration

**Create coordination directory**:
```bash
mkdir -p ~/.swarm_coordination
export SWARM_ROOT_DIR=~/.swarm_coordination
```

**Add to shell profile** (~/.bashrc, ~/.zshrc):
```bash
echo 'export SWARM_ROOT_DIR=~/.swarm_coordination' >> ~/.bashrc
source ~/.bashrc
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SWARM_ROOT_DIR` | Coordination directory | `~/.swarm_coordination` |
| `SWARM_DEBUG` | Enable debug logging | `false` |
| `SWARM_LOG_LEVEL` | Logging level | `INFO` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry endpoint | None |
| `OTEL_SERVICE_NAME` | Service name in traces | `swarm-agent` |

### OpenTelemetry Configuration

**Local Development** (file-based):
```bash
export SWARM_ROOT_DIR=~/.swarm_coordination
# Spans written to telemetry_spans.jsonl
```

**Production** (OTLP export):
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:14268
export OTEL_SERVICE_NAME=swarm-production
export OTEL_RESOURCE_ATTRIBUTES=service.version=1.0.0
```

## Verification

### Installation Check

```bash
# Check dslmodel installation
python -c "import dslmodel; print(dslmodel.__version__)"

# Check CLI availability
dsl --help

# Check SwarmAgent specifically
dsl swarm --help
```

### Dependencies Check

```bash
# Check required packages
python -c "
import typer, rich, pydantic, transitions
print('Core dependencies: OK')
"

# Check OpenTelemetry packages
python -c "
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
print('OpenTelemetry: OK')
"
```

### Functionality Test

```bash
# Test basic functionality
dsl swarm status

# Test span emission
dsl swarm emit 'test.span' --attrs '{"test": true}'

# Test demo workflow
dsl swarm demo ping
```

## Platform-Specific Instructions

### Ubuntu/Debian

**System Dependencies**:
```bash
sudo apt update
sudo apt install python3.12 python3.12-pip python3.12-venv
```

**Install dslmodel**:
```bash
pip3.12 install dslmodel[otel]
```

### CentOS/RHEL

**Enable Python 3.12**:
```bash
sudo dnf install python3.12 python3.12-pip
```

**Install dslmodel**:
```bash
pip3.12 install dslmodel[otel]
```

### macOS

**Using Homebrew**:
```bash
brew install python@3.12
pip3.12 install dslmodel[otel]
```

**Using pyenv**:
```bash
pyenv install 3.12.0
pyenv global 3.12.0
pip install dslmodel[otel]
```

### Windows

**Using Windows Subsystem for Linux (WSL2)**:
```bash
# Install WSL2 if not already installed
wsl --install Ubuntu-22.04

# Inside WSL2
sudo apt update
sudo apt install python3.12 python3.12-pip
pip3.12 install dslmodel[otel]
```

**Using PowerShell** (native Windows):
```powershell
# Install Python 3.12 from python.org
# Then install dslmodel
pip install dslmodel[otel]
```

## Kubernetes Deployment

### Helm Chart

**Add repository**:
```bash
helm repo add dslmodel https://charts.dslmodel.com
helm repo update
```

**Install SwarmAgent**:
```bash
helm install swarm-agents dslmodel/swarm \
  --set agents.roberts.enabled=true \
  --set agents.scrum.enabled=true \
  --set agents.lean.enabled=true
```

### Manual Kubernetes

**Namespace**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: swarm-agents
```

**ConfigMap**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: swarm-config
  namespace: swarm-agents
data:
  SWARM_ROOT_DIR: "/shared/coordination"
  OTEL_SERVICE_NAME: "swarm-k8s"
```

**Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: roberts-agent
  namespace: swarm-agents
spec:
  replicas: 1
  selector:
    matchLabels:
      app: roberts-agent
  template:
    metadata:
      labels:
        app: roberts-agent
    spec:
      containers:
      - name: roberts-agent
        image: dslmodel/swarm:latest
        command: ["dsl", "swarm", "start", "roberts"]
        envFrom:
        - configMapRef:
            name: swarm-config
        volumeMounts:
        - name: coordination-storage
          mountPath: /shared/coordination
      volumes:
      - name: coordination-storage
        persistentVolumeClaim:
          claimName: swarm-coordination-pvc
```

## Cloud Platform Installation

### AWS

**EC2 Instance**:
```bash
# Amazon Linux 2
sudo yum install python3.12 python3.12-pip
pip3.12 install dslmodel[otel]

# Configure CloudWatch integration
export OTEL_EXPORTER_OTLP_ENDPOINT=https://cloudwatch.amazonaws.com/
```

**ECS Task Definition**:
```json
{
  "family": "swarm-agents",
  "containerDefinitions": [
    {
      "name": "roberts-agent",
      "image": "dslmodel/swarm:latest",
      "command": ["dsl", "swarm", "start", "roberts"],
      "environment": [
        {"name": "SWARM_ROOT_DIR", "value": "/tmp/coordination"},
        {"name": "OTEL_SERVICE_NAME", "value": "swarm-ecs"}
      ]
    }
  ]
}
```

### Google Cloud Platform

**Cloud Run**:
```bash
gcloud run deploy swarm-roberts \
  --image dslmodel/swarm:latest \
  --command dsl \
  --args swarm,start,roberts \
  --set-env-vars SWARM_ROOT_DIR=/tmp/coordination
```

**GKE**:
```bash
kubectl apply -f k8s-manifests/
```

### Azure

**Container Instances**:
```bash
az container create \
  --resource-group swarm-rg \
  --name roberts-agent \
  --image dslmodel/swarm:latest \
  --command-line "dsl swarm start roberts" \
  --environment-variables SWARM_ROOT_DIR=/tmp/coordination
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'dslmodel'**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall with user flag
pip install --user dslmodel[otel]
```

**Permission denied errors**
```bash
# Create coordination directory with proper permissions
mkdir -p ~/.swarm_coordination
chmod 755 ~/.swarm_coordination
```

**OpenTelemetry export failures**
```bash
# Test OTLP endpoint connectivity
curl -v $OTEL_EXPORTER_OTLP_ENDPOINT/v1/traces

# Use debug mode
export OTEL_LOG_LEVEL=DEBUG
dsl swarm demo ping
```

### Dependency Conflicts

**Poetry lock conflicts**:
```bash
poetry lock --no-update
poetry install
```

**Pip dependency issues**:
```bash
pip install --upgrade pip
pip install --force-reinstall dslmodel[otel]
```

### Performance Issues

**High memory usage**:
```bash
# Limit trace retention
export SWARM_TRACE_RETENTION_HOURS=24

# Use streaming mode
export SWARM_STREAMING_MODE=true
```

**Slow startup**:
```bash
# Pre-warm agent states
dsl swarm init --preload-agents

# Use optimized imports
export PYTHONOPTIMIZE=1
```

## Next Steps

1. **[Getting Started](GETTING_STARTED.md)** - Quick tutorial
2. **[Architecture Overview](ARCHITECTURE.md)** - System design
3. **[Performance Validation](PERFORMANCE_VALIDATION.md)** - Verify installation
4. **[Production Deployment](PRODUCTION_DEPLOYMENT.md)** - Production setup

## Support

- **Documentation**: [docs/](.)
- **Issues**: [GitHub Issues](https://github.com/seanchatmangpt/dslmodel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/seanchatmangpt/dslmodel/discussions)