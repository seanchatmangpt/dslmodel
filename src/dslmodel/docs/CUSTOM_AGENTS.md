# Custom Agents Guide

## Overview

This guide walks through creating custom SwarmAgent implementations for specific coordination patterns and domain requirements.

## Agent Development Process

### 1. Design Phase

**Define Your Agent's Purpose**:
- What coordination domain does it serve?
- What triggers will it respond to?
- What commands will it emit?
- How does it integrate with existing agents?

**Example Design - DevOps Agent**:
```
Domain: CI/CD Pipeline Coordination
Triggers: deployment requests, test results, security scans
States: IDLE → BUILDING → TESTING → SECURITY_SCAN → DEPLOYING → MONITORING
Emits: deployment commands, notification events, rollback triggers
```

### 2. Implementation Pattern

**Basic agent structure**:
```python
from enum import Enum
from typing import Optional, Dict
from dslmodel.agents.swarm import SwarmAgent, NextCommand, trigger
from dslmodel.agents.swarm.swarm_models import SpanData

class DevOpsState(Enum):
    IDLE = "idle"
    BUILDING = "building"
    TESTING = "testing"
    SECURITY_SCAN = "security_scan"
    DEPLOYING = "deploying"
    MONITORING = "monitoring"
    FAILED = "failed"

class DevOpsAgent(SwarmAgent):
    """CI/CD pipeline coordination agent."""
    
    # Configure span routing
    TRIGGER_MAP = {
        "devops.build.request": "handle_build_request",
        "devops.test.complete": "handle_test_complete",
        "devops.security.complete": "handle_security_complete",
        "devops.deploy.request": "handle_deploy_request",
        "devops.rollback.request": "handle_rollback"
    }
    
    # Filter spans this agent cares about
    LISTEN_FILTER = "devops."
    
    def __init__(self):
        super().__init__(DevOpsState, DevOpsState.IDLE)
    
    @trigger(source=DevOpsState.IDLE, dest=DevOpsState.BUILDING)
    def handle_build_request(self, span: SpanData) -> Optional[NextCommand]:
        """Handle incoming build requests."""
        app_name = span.attributes.get("app_name")
        git_ref = span.attributes.get("git_ref", "main")
        
        self.logger.info(f"Starting build for {app_name} at {git_ref}")
        
        # Emit command to start CI pipeline
        return NextCommand(
            fq_name="ci.pipeline.build",
            args=[
                "--app", app_name,
                "--ref", git_ref,
                "--output-artifacts", f"build-{int(time.time())}"
            ],
            description=f"Build {app_name} from {git_ref}"
        )
    
    @trigger(source=DevOpsState.BUILDING, dest=DevOpsState.TESTING)
    def handle_build_complete(self, span: SpanData) -> Optional[NextCommand]:
        """Transition from build to testing."""
        build_artifacts = span.attributes.get("build_artifacts")
        test_suite = span.attributes.get("test_suite", "all")
        
        return NextCommand(
            fq_name="ci.pipeline.test",
            args=[
                "--artifacts", build_artifacts,
                "--suite", test_suite,
                "--parallel", "true"
            ],
            description=f"Run {test_suite} test suite"
        )
    
    @trigger(source=DevOpsState.TESTING, dest=DevOpsState.SECURITY_SCAN)
    def handle_test_complete(self, span: SpanData) -> Optional[NextCommand]:
        """Move to security scanning after tests pass."""
        test_result = span.attributes.get("test_result")
        
        if test_result == "failed":
            self.current_state = DevOpsState.FAILED
            return NextCommand(
                fq_name="notification.send",
                args=["--type", "test_failure", "--target", "dev-team"],
                description="Notify team of test failures"
            )
        
        # Tests passed, proceed to security scan
        artifacts = span.attributes.get("test_artifacts")
        return NextCommand(
            fq_name="security.scan.start",
            args=[
                "--target", artifacts,
                "--scan-type", "comprehensive",
                "--compliance", "soc2"
            ],
            description="Security compliance scan"
        )
```

### 3. State Machine Design

**Design state transitions carefully**:
```python
# Good: Clear state progression
IDLE → BUILDING → TESTING → DEPLOYING → MONITORING

# Bad: Complex state web
IDLE ↔ BUILDING ↔ TESTING ↔ DEPLOYING ↔ MONITORING ↔ FAILED
```

**Handle error states**:
```python
@trigger(source=[DevOpsState.BUILDING, DevOpsState.TESTING, DevOpsState.DEPLOYING], 
         dest=DevOpsState.FAILED)
def handle_failure(self, span: SpanData) -> Optional[NextCommand]:
    """Handle failures from any operational state."""
    failure_stage = self.current_state.value
    error_details = span.attributes.get("error_details", "Unknown error")
    
    self.logger.error(f"Failure in {failure_stage}: {error_details}")
    
    return NextCommand(
        fq_name="incident.create",
        args=[
            "--severity", "high",
            "--stage", failure_stage,
            "--details", error_details,
            "--assignee", "on-call-engineer"
        ],
        description=f"Create incident for {failure_stage} failure"
    )

@trigger(source=DevOpsState.FAILED, dest=DevOpsState.IDLE)
def handle_recovery(self, span: SpanData) -> Optional[NextCommand]:
    """Reset to idle after incident resolution."""
    incident_id = span.attributes.get("incident_id")
    self.logger.info(f"Recovered from incident {incident_id}")
    return None
```

## Advanced Patterns

### 1. Multi-Agent Coordination

**Chain multiple agents together**:
```python
class QualityGateAgent(SwarmAgent):
    """Quality gate coordination between teams."""
    
    @trigger(source=QualityState.PENDING, dest=QualityState.REVIEWING)
    def handle_review_request(self, span: SpanData) -> Optional[NextCommand]:
        """Coordinate code review process."""
        pr_id = span.attributes.get("pr_id")
        team = span.attributes.get("team")
        
        # Trigger parallel review workflows
        return NextCommand(
            fq_name="review.coordinate",
            args=[
                "--pr", pr_id,
                "--reviewers", f"team:{team}",
                "--require-security-review", "true",
                "--require-architecture-review", "true"
            ],
            description=f"Coordinate review for PR {pr_id}"
        )
    
    @trigger(source=QualityState.REVIEWING, dest=QualityState.APPROVED)
    def handle_reviews_complete(self, span: SpanData) -> Optional[NextCommand]:
        """Forward to DevOps after quality gates pass."""
        pr_id = span.attributes.get("pr_id")
        
        # Trigger DevOps deployment process
        return NextCommand(
            fq_name="devops.build.request",
            args=[
                "--app", span.attributes.get("app_name"),
                "--ref", f"refs/pull/{pr_id}/merge",
                "--triggered-by", "quality-gate"
            ],
            description=f"Trigger deployment for approved PR {pr_id}"
        )
```

### 2. Conditional Logic

**Implement complex coordination logic**:
```python
@trigger(source=DevOpsState.SECURITY_SCAN, dest=DevOpsState.DEPLOYING)
def handle_security_complete(self, span: SpanData) -> Optional[NextCommand]:
    """Handle security scan results with conditional deployment."""
    scan_score = span.attributes.get("security_score", 0)
    critical_vulns = span.attributes.get("critical_vulnerabilities", 0)
    environment = span.attributes.get("target_environment", "staging")
    
    # Production has stricter requirements
    if environment == "production":
        if scan_score < 95 or critical_vulns > 0:
            self.current_state = DevOpsState.FAILED
            return NextCommand(
                fq_name="security.block",
                args=[
                    "--reason", "production_security_threshold",
                    "--score", str(scan_score),
                    "--critical-vulns", str(critical_vulns)
                ],
                description="Block production deployment due to security issues"
            )
    
    # Staging can proceed with warnings
    elif environment == "staging":
        if critical_vulns > 5:  # More lenient for staging
            self.current_state = DevOpsState.FAILED
            return NextCommand(
                fq_name="security.block",
                args=["--reason", "too_many_critical_vulnerabilities"],
                description="Block staging deployment - too many critical vulns"
            )
    
    # Security checks passed, proceed with deployment
    deployment_strategy = "blue-green" if environment == "production" else "rolling"
    
    return NextCommand(
        fq_name="deployment.start",
        args=[
            "--environment", environment,
            "--strategy", deployment_strategy,
            "--security-score", str(scan_score),
            "--auto-rollback", "true" if environment == "production" else "false"
        ],
        description=f"Deploy to {environment} with {deployment_strategy} strategy"
    )
```

### 3. External System Integration

**Integrate with external APIs and services**:
```python
import requests
from typing import Dict, Any

class JiraIntegrationMixin:
    """Mixin for Jira integration capabilities."""
    
    def create_jira_ticket(self, summary: str, description: str, 
                          priority: str = "Medium") -> str:
        """Create Jira ticket and return ticket ID."""
        jira_url = os.getenv("JIRA_URL")
        auth_token = os.getenv("JIRA_TOKEN")
        
        payload = {
            "fields": {
                "project": {"key": "DEVOPS"},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Task"},
                "priority": {"name": priority}
            }
        }
        
        response = requests.post(
            f"{jira_url}/rest/api/3/issue",
            json=payload,
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
            return response.json()["key"]
        else:
            raise Exception(f"Failed to create Jira ticket: {response.text}")

class SlackNotificationMixin:
    """Mixin for Slack notifications."""
    
    def send_slack_notification(self, channel: str, message: str, 
                               severity: str = "info") -> None:
        """Send Slack notification."""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        color_map = {
            "info": "#36a64f",
            "warning": "#ff9500", 
            "error": "#ff0000",
            "success": "#00ff00"
        }
        
        payload = {
            "channel": channel,
            "attachments": [{
                "color": color_map.get(severity, "#36a64f"),
                "text": message,
                "ts": int(time.time())
            }]
        }
        
        requests.post(webhook_url, json=payload)

class EnhancedDevOpsAgent(DevOpsAgent, JiraIntegrationMixin, SlackNotificationMixin):
    """DevOps agent with external integrations."""
    
    @trigger(source=DevOpsState.FAILED, dest=DevOpsState.IDLE)
    def handle_failure_with_integrations(self, span: SpanData) -> Optional[NextCommand]:
        """Handle failures with external system integration."""
        failure_stage = span.attributes.get("failure_stage")
        error_details = span.attributes.get("error_details")
        app_name = span.attributes.get("app_name")
        
        # Create Jira ticket for tracking
        ticket_summary = f"Deployment failure: {app_name} in {failure_stage}"
        ticket_description = f"""
        Application: {app_name}
        Stage: {failure_stage}
        Error: {error_details}
        Timestamp: {span.timestamp}
        Trace ID: {span.trace_id}
        """
        
        try:
            jira_ticket = self.create_jira_ticket(
                summary=ticket_summary,
                description=ticket_description,
                priority="High"
            )
            
            # Send Slack notification
            slack_message = f"""
            🚨 Deployment Failure Alert
            App: {app_name}
            Stage: {failure_stage}
            Jira Ticket: {jira_ticket}
            Error: {error_details}
            """
            
            self.send_slack_notification(
                channel="#devops-alerts",
                message=slack_message,
                severity="error"
            )
            
            self.logger.info(f"Created Jira ticket {jira_ticket} for failure")
            
        except Exception as e:
            self.logger.error(f"Failed to create integrations: {e}")
        
        return None
```

## Semantic Conventions

### 1. Define Agent-Specific Schemas

**Create Weaver schema** (`agent_schemas/devops.yaml`):
```yaml
groups:
  - id: devops
    prefix: devops
    type: span
    brief: 'DevOps pipeline coordination spans'

spans:
  - id: devops.build
    type: span
    span_kind: internal
    prefix: devops.build
    brief: 'Build pipeline operations'
    attributes:
      - id: app_name
        type: string
        requirement_level: required
        brief: 'Application being built'
      - id: git_ref
        type: string
        requirement_level: required
        brief: 'Git reference being built'
      - id: build_artifacts
        type: string
        requirement_level: optional
        brief: 'Build artifact locations'

  - id: devops.test
    type: span
    span_kind: internal
    prefix: devops.test
    brief: 'Test execution operations'
    attributes:
      - id: test_suite
        type:
          allow_custom_values: true
          members:
            - id: unit
              value: 'unit'
            - id: integration
              value: 'integration'
            - id: e2e
              value: 'e2e'
            - id: performance
              value: 'performance'
      - id: test_result
        type:
          members:
            - id: passed
              value: 'passed'
            - id: failed
              value: 'failed'
            - id: skipped
              value: 'skipped'

  - id: devops.security
    type: span
    span_kind: internal
    prefix: devops.security
    brief: 'Security scanning operations'
    attributes:
      - id: security_score
        type: int
        requirement_level: required
        brief: 'Security scan score (0-100)'
      - id: critical_vulnerabilities
        type: int
        requirement_level: required
        brief: 'Number of critical vulnerabilities'
      - id: scan_type
        type:
          members:
            - id: sast
              value: 'sast'
            - id: dast
              value: 'dast'
            - id: dependency
              value: 'dependency'
            - id: comprehensive
              value: 'comprehensive'
```

### 2. Generate Validation Models

**Generate Pydantic models from schema**:
```bash
weaver registry generate-code \
  --registry agent_schemas/ \
  --output src/dslmodel/otel/models/ \
  --target pydantic
```

**Use generated models in agent**:
```python
from dslmodel.otel.models.devops_attributes import (
    DevOpsBuildAttributes,
    DevOpsTestAttributes,
    DevOpsSecurityAttributes
)

class DevOpsAgent(SwarmAgent):
    def validate_span_attributes(self, span: SpanData) -> bool:
        """Validate span attributes against schema."""
        try:
            if span.name.startswith("devops.build"):
                DevOpsBuildAttributes(**span.attributes)
            elif span.name.startswith("devops.test"):
                DevOpsTestAttributes(**span.attributes)
            elif span.name.startswith("devops.security"):
                DevOpsSecurityAttributes(**span.attributes)
            return True
        except ValidationError as e:
            self.logger.warning(f"Span validation failed: {e}")
            return False
```

## Testing Custom Agents

### 1. Unit Testing

**Test agent logic in isolation**:
```python
import pytest
from unittest.mock import Mock
from dslmodel.agents.examples.devops_agent import DevOpsAgent, DevOpsState

class TestDevOpsAgent:
    def test_build_request_transition(self):
        """Test build request handling."""
        agent = DevOpsAgent()
        
        # Create test span
        span = Mock()
        span.attributes = {
            "app_name": "test-app",
            "git_ref": "feature/test-branch"
        }
        
        # Handle build request
        result = agent.handle_build_request(span)
        
        # Verify state transition
        assert agent.current_state == DevOpsState.BUILDING
        
        # Verify command emission
        assert result is not None
        assert result.fq_name == "ci.pipeline.build"
        assert "--app" in result.args
        assert "test-app" in result.args
    
    def test_security_failure_handling(self):
        """Test security scan failure handling."""
        agent = DevOpsAgent()
        agent.current_state = DevOpsState.SECURITY_SCAN
        
        span = Mock()
        span.attributes = {
            "security_score": 60,  # Below threshold
            "critical_vulnerabilities": 3,
            "target_environment": "production"
        }
        
        result = agent.handle_security_complete(span)
        
        # Should transition to failed state
        assert agent.current_state == DevOpsState.FAILED
        
        # Should emit security block command
        assert result.fq_name == "security.block"
    
    def test_conditional_deployment_logic(self):
        """Test conditional deployment based on environment."""
        agent = DevOpsAgent()
        agent.current_state = DevOpsState.SECURITY_SCAN
        
        # Test staging deployment (more lenient)
        staging_span = Mock()
        staging_span.attributes = {
            "security_score": 85,
            "critical_vulnerabilities": 2,
            "target_environment": "staging"
        }
        
        result = agent.handle_security_complete(staging_span)
        
        assert agent.current_state == DevOpsState.DEPLOYING
        assert result.fq_name == "deployment.start"
        assert "rolling" in result.args  # Staging uses rolling deployment
```

### 2. Integration Testing

**Test agent coordination flows**:
```python
def test_devops_quality_coordination():
    """Test DevOps and Quality agent coordination."""
    devops_agent = DevOpsAgent()
    quality_agent = QualityGateAgent()
    
    # Simulate quality gate approval
    quality_span = create_test_span(
        "quality.review.complete",
        {"pr_id": "123", "app_name": "test-app", "reviews_approved": True}
    )
    
    quality_result = quality_agent.forward(quality_span)
    
    # Should emit DevOps build request
    assert quality_result.fq_name == "devops.build.request"
    
    # Convert command to span for DevOps agent
    devops_span = command_to_span(quality_result)
    devops_result = devops_agent.forward(devops_span)
    
    # DevOps should transition to building and emit CI command
    assert devops_agent.current_state == DevOpsState.BUILDING
    assert devops_result.fq_name == "ci.pipeline.build"
```

### 3. Performance Testing

**Test agent performance under load**:
```python
import time
import concurrent.futures

def test_agent_performance():
    """Test agent performance with concurrent span processing."""
    agent = DevOpsAgent()
    
    def process_span(span_data):
        span = create_test_span("devops.build.request", span_data)
        start_time = time.time()
        result = agent.forward(span)
        processing_time = (time.time() - start_time) * 1000
        return processing_time, result
    
    # Generate test data
    test_spans = [
        {"app_name": f"app-{i}", "git_ref": "main"} 
        for i in range(100)
    ]
    
    # Process concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(process_span, span_data) 
            for span_data in test_spans
        ]
        
        results = [future.result() for future in futures]
    
    # Analyze performance
    processing_times = [r[0] for r in results]
    avg_time = sum(processing_times) / len(processing_times)
    max_time = max(processing_times)
    
    print(f"Average processing time: {avg_time:.2f}ms")
    print(f"Maximum processing time: {max_time:.2f}ms")
    
    # Assert performance targets
    assert avg_time < 10.0  # Average < 10ms
    assert max_time < 50.0  # Max < 50ms
```

## Agent Registration

### 1. CLI Integration

**Register agent with CLI** (`src/dslmodel/commands/swarm.py`):
```python
# Add to agent registry
AVAILABLE_AGENTS = {
    "roberts": ("dslmodel.agents.examples.roberts_agent", "RobertsAgent"),
    "scrum": ("dslmodel.agents.examples.scrum_agent", "ScrumAgent"),
    "lean": ("dslmodel.agents.examples.lean_agent", "LeanAgent"),
    "devops": ("dslmodel.agents.examples.devops_agent", "DevOpsAgent"),  # New agent
}

@app.command("start")
def start_agent(
    agent_name: str = typer.Argument(..., help="Agent to start"),
    background: bool = typer.Option(False, "--background", help="Run in background")
):
    """Start a specific agent."""
    if agent_name not in AVAILABLE_AGENTS:
        typer.echo(f"Unknown agent: {agent_name}")
        typer.echo(f"Available agents: {', '.join(AVAILABLE_AGENTS.keys())}")
        raise typer.Exit(1)
    
    # Dynamic import and start
    module_path, class_name = AVAILABLE_AGENTS[agent_name]
    module = importlib.import_module(module_path)
    agent_class = getattr(module, class_name)
    
    agent = agent_class()
    agent.run()
```

### 2. Package Distribution

**Include in package** (`pyproject.toml`):
```toml
[tool.poetry.extras]
devops = ["jira", "slack-sdk", "kubernetes"]

[tool.poetry.group.devops]
optional = true

[tool.poetry.group.devops.dependencies]
jira = "^3.4.0"
slack-sdk = "^3.20.0"
kubernetes = "^25.3.0"
```

## Best Practices

### 1. Design Principles

- **Single Responsibility**: Each agent handles one coordination domain
- **Clear State Machines**: Avoid complex state webs
- **Fail Gracefully**: Handle errors and provide recovery paths
- **Observable**: Emit rich telemetry for debugging
- **Testable**: Design for unit and integration testing

### 2. Performance Considerations

- **Minimal State**: Keep agent state small and serializable
- **Efficient Triggers**: Use specific span filters to reduce processing
- **Async Operations**: Use async/await for I/O operations
- **Resource Limits**: Implement timeouts and circuit breakers

### 3. Security Guidelines

- **Input Validation**: Validate all span attributes
- **Secure Secrets**: Use secret management for external APIs
- **Access Control**: Implement proper RBAC for agent actions
- **Audit Logging**: Log all coordination decisions

### 4. Documentation Standards

- **Clear Docstrings**: Document trigger conditions and state transitions
- **Examples**: Provide working examples and test cases
- **Diagrams**: Include state machine and coordination flow diagrams
- **Troubleshooting**: Document common issues and solutions

## Next Steps

- **[Performance Validation](PERFORMANCE_VALIDATION.md)** - Test your agent performance
- **[Production Deployment](PRODUCTION_DEPLOYMENT.md)** - Deploy custom agents
- **[Troubleshooting](TROUBLESHOOTING.md)** - Debug agent issues