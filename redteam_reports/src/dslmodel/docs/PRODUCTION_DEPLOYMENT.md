# Production Deployment

## Overview

This guide covers deploying SwarmAgent systems in production environments with proper monitoring, scaling, and reliability considerations.

## Deployment Architectures

### Single-Node Deployment

**For small teams (1-10 people)**:
```bash
# Docker Compose deployment
version: '3.8'
services:
  roberts-agent:
    image: dslmodel/swarm:latest
    command: dsl swarm start roberts
    environment:
      - SWARM_ROOT_DIR=/shared/coordination
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:14268
    volumes:
      - coordination_data:/shared/coordination
    restart: unless-stopped
    
  scrum-agent:
    image: dslmodel/swarm:latest
    command: dsl swarm start scrum
    environment:
      - SWARM_ROOT_DIR=/shared/coordination
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:14268
    volumes:
      - coordination_data:/shared/coordination
    restart: unless-stopped
    
  lean-agent:
    image: dslmodel/swarm:latest
    command: dsl swarm start lean
    environment:
      - SWARM_ROOT_DIR=/shared/coordination
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:14268
    volumes:
      - coordination_data:/shared/coordination
    restart: unless-stopped

volumes:
  coordination_data:
```

### Kubernetes Deployment

**For teams (10-100 people)**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: swarm-production
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: swarm-config
  namespace: swarm-production
data:
  SWARM_ROOT_DIR: "/shared/coordination"
  OTEL_SERVICE_NAME: "swarm-production"
  OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel-collector:4317"
  SWARM_LOG_LEVEL: "INFO"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: roberts-agent
  namespace: swarm-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: roberts-agent
  template:
    metadata:
      labels:
        app: roberts-agent
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      containers:
      - name: roberts-agent
        image: dslmodel/swarm:v1.0.0
        command: ["dsl", "swarm", "start", "roberts"]
        envFrom:
        - configMapRef:
            name: swarm-config
        ports:
        - containerPort: 8080
          name: metrics
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: coordination-storage
          mountPath: /shared/coordination
      volumes:
      - name: coordination-storage
        persistentVolumeClaim:
          claimName: swarm-coordination-pvc
```

### Cloud-Native Deployment

**For enterprises (100+ people)**:
```yaml
# AWS EKS with Fargate
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swarm-agents
  namespace: swarm-production
spec:
  replicas: 10
  selector:
    matchLabels:
      app: swarm-agents
  template:
    metadata:
      labels:
        app: swarm-agents
    spec:
      serviceAccountName: swarm-agent-sa
      containers:
      - name: swarm-agent
        image: dslmodel/swarm:v1.0.0
        env:
        - name: AWS_REGION
          value: "us-west-2"
        - name: SWARM_STORAGE_TYPE
          value: "s3"
        - name: SWARM_S3_BUCKET
          value: "company-swarm-coordination"
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "https://api.honeycomb.io"
        - name: OTEL_EXPORTER_OTLP_HEADERS
          valueFrom:
            secretKeyRef:
              name: otel-secret
              key: honeycomb-key
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: swarm-agent-sa
  namespace: swarm-production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/SwarmAgentRole
```

## Observability Stack

### OpenTelemetry Collector

**OTEL Collector configuration** (`otel-collector-config.yaml`):
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  
  attributes:
    actions:
      - key: service.name
        value: swarm-production
        action: upsert
      - key: deployment.environment
        value: production
        action: upsert

exporters:
  jaeger:
    endpoint: jaeger-collector:14250
    tls:
      insecure: true
  
  prometheus:
    endpoint: "0.0.0.0:8889"
    
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [attributes, batch]
      exporters: [jaeger, logging]
    
    metrics:
      receivers: [otlp]
      processors: [attributes, batch]
      exporters: [prometheus]
```

### Monitoring Dashboard

**Grafana dashboard configuration**:
```json
{
  "dashboard": {
    "title": "SwarmAgent Production Monitoring",
    "panels": [
      {
        "title": "Agent Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"swarm-agents\"}",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Coordination Throughput",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(swarm_coordination_events_total[5m])",
            "legendFormat": "Events/sec"
          }
        ]
      },
      {
        "title": "Processing Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(swarm_processing_duration_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(swarm_processing_duration_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{pod=~\".*swarm.*\"} / 1024 / 1024",
            "legendFormat": "{{pod}}"
          }
        ]
      }
    ]
  }
}
```

### Alerting Rules

**Prometheus alerting rules** (`swarm-alerts.yml`):
```yaml
groups:
- name: swarm-agents
  rules:
  - alert: SwarmAgentDown
    expr: up{job="swarm-agents"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "SwarmAgent instance is down"
      description: "Agent {{ $labels.instance }} has been down for more than 1 minute"

  - alert: HighCoordinationLatency
    expr: histogram_quantile(0.95, rate(swarm_processing_duration_bucket[5m])) > 100
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High coordination latency detected"
      description: "95th percentile latency is {{ $value }}ms"

  - alert: LowCoordinationThroughput
    expr: rate(swarm_coordination_events_total[5m]) < 10
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Low coordination throughput"
      description: "Coordination events are below 10/sec for 10 minutes"

  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes{pod=~".*swarm.*"} / container_spec_memory_limit_bytes > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on SwarmAgent"
      description: "Memory usage is {{ $value | humanizePercentage }} on {{ $labels.pod }}"
```

## Scaling Strategies

### Horizontal Scaling

**Auto-scaling based on coordination load**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: swarm-agents-hpa
  namespace: swarm-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: swarm-agents
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: swarm_coordination_events_per_second
      target:
        type: AverageValue
        averageValue: "50"
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling

**Resource allocation based on load**:
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"  # Allow burst for high coordination load
    cpu: "1000m"     # Scale up for complex workflows
```

### Geographic Distribution

**Multi-region deployment**:
```yaml
# US-West region
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swarm-agents-west
spec:
  template:
    spec:
      nodeSelector:
        topology.kubernetes.io/region: us-west-2
      containers:
      - name: swarm-agent
        env:
        - name: SWARM_REGION
          value: "us-west"
        - name: SWARM_COORDINATION_TOPIC
          value: "coordination-us-west"

---
# EU region  
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swarm-agents-eu
spec:
  template:
    spec:
      nodeSelector:
        topology.kubernetes.io/region: eu-central-1
      containers:
      - name: swarm-agent
        env:
        - name: SWARM_REGION
          value: "eu-central"
        - name: SWARM_COORDINATION_TOPIC
          value: "coordination-eu-central"
```

## Data Management

### Persistent Storage

**Coordination data persistence**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: swarm-coordination-pvc
  namespace: swarm-production
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: efs-sc
  resources:
    requests:
      storage: 100Gi
```

### Backup Strategy

**Automated coordination data backup**:
```bash
#!/bin/bash
# backup-coordination.sh

BACKUP_DIR="/backups/swarm-coordination"
COORDINATION_DIR="/shared/coordination"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create backup
tar -czf "${BACKUP_DIR}/coordination-${TIMESTAMP}.tar.gz" "${COORDINATION_DIR}"

# Upload to cloud storage
aws s3 cp "${BACKUP_DIR}/coordination-${TIMESTAMP}.tar.gz" \
  "s3://company-backups/swarm-coordination/"

# Retain only last 30 days
find "${BACKUP_DIR}" -name "coordination-*.tar.gz" -mtime +30 -delete
```

**Kubernetes CronJob for backups**:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: swarm-backup
  namespace: swarm-production
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: alpine/git
            command:
            - /bin/sh
            - -c
            - |
              apk add --no-cache tar gzip aws-cli
              /scripts/backup-coordination.sh
            volumeMounts:
            - name: coordination-data
              mountPath: /shared/coordination
            - name: backup-scripts
              mountPath: /scripts
          volumes:
          - name: coordination-data
            persistentVolumeClaim:
              claimName: swarm-coordination-pvc
          - name: backup-scripts
            configMap:
              name: backup-scripts
              defaultMode: 0755
          restartPolicy: OnFailure
```

## Security Configuration

### Network Security

**Network policies**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: swarm-agents-netpol
  namespace: swarm-production
spec:
  podSelector:
    matchLabels:
      app: swarm-agents
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: otel-system
    ports:
    - protocol: TCP
      port: 4317
```

### Access Control

**RBAC configuration**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: swarm-agent-sa
  namespace: swarm-production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: swarm-agent-role
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["events"]
  verbs: ["create"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: swarm-agent-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: swarm-agent-role
subjects:
- kind: ServiceAccount
  name: swarm-agent-sa
  namespace: swarm-production
```

### Secrets Management

**Using external secrets**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: swarm-production
spec:
  provider:
    vault:
      server: "https://vault.company.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "swarm-agent"
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: swarm-otel-secret
  namespace: swarm-production
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: otel-secret
    creationPolicy: Owner
  data:
  - secretKey: honeycomb-key
    remoteRef:
      key: swarm/otel
      property: honeycomb_api_key
```

## Disaster Recovery

### High Availability Setup

**Multi-AZ deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swarm-agents-ha
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - swarm-agents
              topologyKey: topology.kubernetes.io/zone
```

### Recovery Procedures

**Automated recovery script**:
```bash
#!/bin/bash
# disaster-recovery.sh

set -e

echo "Starting SwarmAgent disaster recovery..."

# 1. Check agent health
echo "Checking agent health..."
if ! kubectl get pods -n swarm-production -l app=swarm-agents | grep Running; then
    echo "No healthy agents found, starting recovery..."
    
    # 2. Restore from backup
    echo "Restoring coordination data..."
    LATEST_BACKUP=$(aws s3 ls s3://company-backups/swarm-coordination/ | sort | tail -n 1 | awk '{print $4}')
    aws s3 cp "s3://company-backups/swarm-coordination/${LATEST_BACKUP}" /tmp/
    
    # 3. Extract backup to coordination volume
    kubectl exec -n swarm-production deployment/swarm-agents -- \
        tar -xzf "/tmp/${LATEST_BACKUP}" -C /shared/coordination/
    
    # 4. Restart agents
    echo "Restarting agents..."
    kubectl rollout restart deployment/swarm-agents -n swarm-production
    kubectl rollout status deployment/swarm-agents -n swarm-production
    
    # 5. Verify recovery
    echo "Verifying recovery..."
    kubectl exec -n swarm-production deployment/swarm-agents -- \
        dsl swarm status
fi

echo "Disaster recovery completed successfully"
```

## Performance Tuning

### JVM Tuning (if using JVM-based tools)

```bash
export JAVA_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

### Resource Optimization

**Memory optimization**:
```yaml
containers:
- name: swarm-agent
  resources:
    requests:
      memory: "256Mi"  # Increased for production
      cpu: "200m"
    limits:
      memory: "1Gi"    # Allow for coordination bursts
      cpu: "1000m"
  env:
  - name: SWARM_MEMORY_LIMIT
    valueFrom:
      resourceFieldRef:
        resource: limits.memory
  - name: SWARM_CPU_LIMIT
    valueFrom:
      resourceFieldRef:
        resource: limits.cpu
```

## Maintenance Procedures

### Rolling Updates

**Zero-downtime deployment**:
```bash
# Update agent image
kubectl set image deployment/swarm-agents swarm-agent=dslmodel/swarm:v1.1.0 -n swarm-production

# Monitor rollout
kubectl rollout status deployment/swarm-agents -n swarm-production

# Verify coordination continues
dsl swarm validate --production
```

### Health Checks

**Automated health monitoring**:
```python
#!/usr/bin/env python3
# health-check.py

import requests
import sys
import time

def check_agent_health():
    try:
        response = requests.get('http://localhost:8080/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get('status') == 'healthy':
                return True
        return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def check_coordination():
    try:
        # Check last coordination activity
        response = requests.get('http://localhost:8080/metrics', timeout=5)
        if 'swarm_coordination_events_total' in response.text:
            return True
        return False
    except Exception as e:
        print(f"Coordination check failed: {e}")
        return False

if __name__ == "__main__":
    if check_agent_health() and check_coordination():
        print("Health check passed")
        sys.exit(0)
    else:
        print("Health check failed")
        sys.exit(1)
```

## Next Steps

- **[Performance Validation](PERFORMANCE_VALIDATION.md)** - Validate production performance
- **[Troubleshooting](TROUBLESHOOTING.md)** - Debug production issues
- **[Custom Agents](CUSTOM_AGENTS.md)** - Extend for specific use cases