# DSL Present Command

## Overview
The `present` command provides presentation and reporting capabilities for DSLModel system demonstrations and analysis.

## Usage
```bash
# Generate system presentation
dsl present system

# Generate agent presentation
dsl present agent

# Generate telemetry presentation
dsl present telemetry

# Generate security presentation
dsl present security

# Generate performance presentation
dsl present performance

# Generate comprehensive report
dsl present report

# Create presentation slides
dsl present slides

# Generate executive summary
dsl present executive-summary

# Run presentation demo
dsl present demo
```

## Subcommands

### system
Generate system presentation:
```bash
dsl present system --output "system_presentation.pdf"
```

### agent
Generate agent presentation:
```bash
dsl present agent --agent-id "agent-123" --output "agent_presentation.pdf"
```

### telemetry
Generate telemetry presentation:
```bash
dsl present telemetry --duration 300 --output "telemetry_presentation.pdf"
```

### security
Generate security presentation:
```bash
dsl present security --scan-results "security_scan.json" --output "security_presentation.pdf"
```

### performance
Generate performance presentation:
```bash
dsl present performance --metrics "response-time,throughput" --output "performance_presentation.pdf"
```

### report
Generate comprehensive report:
```bash
dsl present report --format "pdf" --output "comprehensive_report.pdf"
```

### slides
Create presentation slides:
```bash
dsl present slides --template "executive" --output "presentation_slides.pptx"
```

### executive-summary
Generate executive summary:
```bash
dsl present executive-summary --output "executive_summary.pdf"
```

### demo
Run presentation demonstration:
```bash
dsl present demo
```

## Presentation Features
- **Automated Generation**: AI-powered presentation creation
- **Multiple Formats**: PDF, PowerPoint, and web formats
- **Custom Templates**: Professional presentation templates
- **Data Visualization**: Charts, graphs, and metrics visualization

## Context
The presentation system provides automated generation of professional presentations and reports, enabling effective communication of DSLModel capabilities and results. 