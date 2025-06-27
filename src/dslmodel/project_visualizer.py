#!/usr/bin/env python3
"""
Project Visualizer - Comprehensive visualization of DSLModel project for v3 consolidation

This module provides multiple visualization approaches:
1. Architecture Overview - Component relationships
2. Dependency Graph - Module dependencies
3. Feature Map - Capabilities and integrations
4. Data Flow - How data moves through the system
5. API Surface - Public interfaces
6. Evolution Timeline - Project growth
"""

import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import typer
from rich.console import Console
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import track

app = typer.Typer()
console = Console()


@dataclass
class ProjectComponent:
    name: str
    type: str  # core, mixin, example, utility, test
    path: Path
    imports: Set[str]
    exports: Set[str]
    dependencies: Set[str]
    features: List[str]
    complexity: int
    lines_of_code: int


class ProjectVisualizer:
    """Comprehensive project visualization system"""
    
    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.components: Dict[str, ProjectComponent] = {}
        self.mermaid_diagrams: Dict[str, str] = {}
        
    def analyze_project(self):
        """Analyze entire project structure"""
        console.print("[cyan]🔍 Analyzing DSLModel project structure...[/cyan]")
        
        # Core components
        self._analyze_core_components()
        
        # Mixins
        self._analyze_mixins()
        
        # Examples
        self._analyze_examples()
        
        # Utilities
        self._analyze_utilities()
        
        # Tests
        self._analyze_tests()
        
        console.print(f"[green]✅ Analyzed {len(self.components)} components[/green]")
    
    def _analyze_core_components(self):
        """Analyze core DSL components"""
        core_dir = self.project_root / "src" / "dslmodel"
        core_files = [
            "dsl_models.py",
            "workflow.py", 
            "cli.py",
            "api.py"
        ]
        
        for file_name in core_files:
            file_path = core_dir / file_name
            if file_path.exists():
                self._analyze_python_file(file_path, "core")
    
    def _analyze_mixins(self):
        """Analyze mixin components"""
        mixins_dir = self.project_root / "src" / "dslmodel" / "mixins"
        if mixins_dir.exists():
            for mixin_file in mixins_dir.glob("*.py"):
                if mixin_file.name != "__init__.py":
                    self._analyze_python_file(mixin_file, "mixin")
    
    def _analyze_examples(self):
        """Analyze example components"""
        examples_dir = self.project_root / "src" / "dslmodel" / "examples"
        if examples_dir.exists():
            for example_file in examples_dir.glob("*.py"):
                if example_file.name != "__init__.py":
                    self._analyze_python_file(example_file, "example")
    
    def _analyze_utilities(self):
        """Analyze utility components"""
        utils_dir = self.project_root / "src" / "dslmodel" / "utils"
        if utils_dir.exists():
            for util_file in utils_dir.glob("*.py"):
                if util_file.name != "__init__.py":
                    self._analyze_python_file(util_file, "utility")
    
    def _analyze_tests(self):
        """Analyze test components"""
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.glob("test_*.py"):
                self._analyze_python_file(test_file, "test")
    
    def _analyze_python_file(self, file_path: Path, component_type: str):
        """Analyze a single Python file"""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            imports = set()
            exports = set()
            features = []
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                elif isinstance(node, ast.ClassDef):
                    exports.add(node.name)
                    # Extract class features
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if not item.name.startswith('_'):
                                features.append(f"{node.name}.{item.name}")
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):
                        exports.add(node.name)
            
            # Calculate complexity (simplified)
            complexity = len([n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))])
            
            # Count lines
            lines_of_code = len(content.splitlines())
            
            # Extract dependencies
            dependencies = {imp for imp in imports if imp.startswith(('dslmodel', 'src.dslmodel'))}
            
            component = ProjectComponent(
                name=file_path.stem,
                type=component_type,
                path=file_path,
                imports=imports,
                exports=exports,
                dependencies=dependencies,
                features=features,
                complexity=complexity,
                lines_of_code=lines_of_code
            )
            
            self.components[component.name] = component
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not analyze {file_path}: {e}[/yellow]")
    
    def generate_architecture_mermaid(self) -> str:
        """Generate architecture overview Mermaid diagram"""
        console.print("[cyan]📐 Generating architecture diagram...[/cyan]")
        
        mermaid = """graph TB
    subgraph "Core Components"
        DSLModel[DSLModel<br/>Base Class]
        Workflow[Workflow<br/>Engine]
        CLI[CLI<br/>Interface]
        API[API<br/>Server]
    end
    
    subgraph "Mixins"
        JinjaMixin[Jinja DSL<br/>Mixin]
        DSPyMixin[DSPy DSL<br/>Mixin]
        FileMixin[File Handler<br/>Mixin]
        FSMMixin[FSM<br/>Mixin]
        ValidationMixin[Validation<br/>Mixin]
    end
    
    subgraph "AI Integration"
        DSPyModules[DSPy<br/>Modules]
        Prompts[Prompt<br/>Templates]
        AIAssistants[AI<br/>Assistants]
    end
    
    subgraph "Examples"
        Gherkin[Gherkin<br/>Models]
        SIPOC[SIPOC<br/>Models]
        BDD[BDD<br/>Models]
        N8N[N8N Node<br/>Generator]
        YAWL[YAWL<br/>Models]
    end
    
    subgraph "Infrastructure"
        OTEL[OpenTelemetry<br/>Integration]
        Weaver[Semantic<br/>Conventions]
        Monitor[OTEL<br/>Monitor]
    end
    
    %% Core relationships
    DSLModel --> JinjaMixin
    DSLModel --> DSPyMixin
    DSLModel --> FileMixin
    DSLModel --> FSMMixin
    DSLModel --> ValidationMixin
    
    %% Workflow relationships
    Workflow --> DSLModel
    CLI --> Workflow
    API --> Workflow
    
    %% AI relationships
    DSPyMixin --> DSPyModules
    DSPyModules --> Prompts
    DSPyModules --> AIAssistants
    
    %% Example relationships
    Gherkin --> DSLModel
    SIPOC --> DSLModel
    BDD --> DSLModel
    N8N --> DSLModel
    YAWL --> DSLModel
    
    %% Infrastructure relationships
    OTEL --> Monitor
    Weaver --> OTEL
    Monitor --> API
    
    %% Styling
    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef mixin fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef ai fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef example fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef infra fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class DSLModel,Workflow,CLI,API core
    class JinjaMixin,DSPyMixin,FileMixin,FSMMixin,ValidationMixin mixin
    class DSPyModules,Prompts,AIAssistants ai
    class Gherkin,SIPOC,BDD,N8N,YAWL example
    class OTEL,Weaver,Monitor infra
"""
        
        self.mermaid_diagrams['architecture'] = mermaid
        return mermaid
    
    def generate_dependency_mermaid(self) -> str:
        """Generate dependency graph Mermaid diagram"""
        console.print("[cyan]🔗 Generating dependency graph...[/cyan]")
        
        # Build dependency relationships
        deps = []
        for name, component in self.components.items():
            if component.type in ['core', 'mixin', 'utility']:
                for dep in component.dependencies:
                    dep_name = dep.split('.')[-1]
                    if dep_name in self.components:
                        deps.append(f"    {name} --> {dep_name}")
        
        mermaid = f"""graph LR
    subgraph "Core Layer"
        dsl_models[dsl_models]
        workflow[workflow]
        cli[cli]
        api[api]
    end
    
    subgraph "Mixin Layer"
        jinja_dsl_mixin[jinja_dsl_mixin]
        dspy_dsl_mixin[dspy_dsl_mixin]
        file_handler_mixin[file_handler_mixin]
        fsm_mixin[fsm_mixin]
        validation_mixin[validation_mixin]
    end
    
    subgraph "Utility Layer"
        dspy_tools[dspy_tools]
        source_tools[source_tools]
        file_tools[file_tools]
    end
    
    subgraph "Integration Layer"
        weaver_multilayer[weaver_multilayer]
        otel_gap_analyzer[otel_gap_analyzer]
        claude_code_otel_monitor[claude_code_otel_monitor]
    end
    
{chr(10).join(deps)}
    
    classDef core fill:#bbdefb,stroke:#1565c0,stroke-width:3px
    classDef mixin fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
    classDef util fill:#a5d6a7,stroke:#2e7d32,stroke-width:2px
    classDef integration fill:#ffcc80,stroke:#ef6c00,stroke-width:2px
"""
        
        self.mermaid_diagrams['dependencies'] = mermaid
        return mermaid
    
    def generate_feature_map_mermaid(self) -> str:
        """Generate feature map Mermaid diagram"""
        console.print("[cyan]🗺️ Generating feature map...[/cyan]")
        
        mermaid = """mindmap
  root((DSLModel v3))
    Model Creation
      Declarative Models
        Pydantic BaseModel
        Field Validation
        Type Safety
      AI Generation
        from_prompt()
        from_template()
        from_signature()
      Template Rendering
        Jinja2 Integration
        Dynamic Fields
        Nested Templates
    
    Workflow Engine
      Hierarchical Structure
        Workflows
        Jobs
        Actions
      Execution
        Dependency Resolution
        Conditional Logic
        Retry Handling
        SLA Tracking
      Configuration
        YAML Based
        Environment Management
        Context Passing
    
    AI Integration
      DSPy Framework
        Language Models
        Prompt Optimization
        Chain of Thought
      Model Support
        OpenAI GPT-4
        Claude
        Local Models
      AI Assistants
        Context Management
        Tool Integration
        Memory Systems
    
    File Operations
      Serialization
        YAML
        JSON
        TOML
      Validation
        Schema Validation
        Type Checking
        Custom Rules
      Persistence
        Load/Save
        Format Detection
        Encoding Handling
    
    State Management
      FSM Integration
        State Definitions
        Transitions
        Guards
        Callbacks
      Event System
        Triggers
        Actions
        History
    
    Developer Experience
      CLI Tools
        Project Init
        Model Generation
        Workflow Execution
      API Server
        FastAPI Integration
        Auto Documentation
        REST Endpoints
      Testing
        90% Coverage
        Fixtures
        Mocking
    
    Observability
      OpenTelemetry
        Spans
        Metrics
        Traces
      Semantic Conventions
        Multi-layer System
        Validation
        Gap Analysis
      Monitoring
        Real-time Tracking
        Compliance Checking
        80/20 Analysis
    
    Examples
      Domain Models
        Gherkin/BDD
        SIPOC
        CCS Graph
      Integrations
        N8N Nodes
        YAWL Workflows
        Agent Models
      Templates
        Project Templates
        Model Templates
        Workflow Templates
"""
        
        self.mermaid_diagrams['feature_map'] = mermaid
        return mermaid
    
    def generate_data_flow_mermaid(self) -> str:
        """Generate data flow Mermaid diagram"""
        console.print("[cyan]🌊 Generating data flow diagram...[/cyan]")
        
        mermaid = """sequenceDiagram
    participant User
    participant CLI
    participant DSLModel
    participant Mixins
    participant AI
    participant Storage
    participant OTEL
    
    User->>CLI: Create model from prompt
    CLI->>DSLModel: Initialize with prompt
    DSLModel->>AI: Generate via DSPy
    AI-->>DSLModel: Return generated fields
    DSLModel->>Mixins: Apply transformations
    Mixins-->>DSLModel: Enhanced model
    DSLModel->>Storage: Serialize to YAML
    Storage-->>User: Model file created
    
    Note over DSLModel,OTEL: Telemetry Collection
    DSLModel->>OTEL: Emit spans
    OTEL->>OTEL: Validate conventions
    
    User->>CLI: Execute workflow
    CLI->>DSLModel: Load workflow
    DSLModel->>Mixins: Validate structure
    loop For each job
        DSLModel->>DSLModel: Resolve dependencies
        DSLModel->>DSLModel: Execute actions
        DSLModel->>OTEL: Track execution
    end
    DSLModel-->>User: Workflow results
"""
        
        self.mermaid_diagrams['data_flow'] = mermaid
        return mermaid
    
    def generate_evolution_timeline_mermaid(self) -> str:
        """Generate project evolution timeline"""
        console.print("[cyan]📅 Generating evolution timeline...[/cyan]")
        
        mermaid = """gantt
    title DSLModel Evolution to v3
    dateFormat YYYY-MM-DD
    section Core Development
    Base DSLModel Class           :done, core1, 2024-01-01, 30d
    Mixin Architecture            :done, core2, after core1, 45d
    Workflow Engine               :done, core3, after core2, 60d
    
    section AI Integration
    DSPy Integration              :done, ai1, 2024-03-01, 30d
    Prompt Templates              :done, ai2, after ai1, 20d
    AI Assistants                 :done, ai3, after ai2, 40d
    
    section Infrastructure
    CLI Development               :done, infra1, 2024-02-15, 25d
    API Server                    :done, infra2, after infra1, 30d
    Testing Framework             :done, infra3, 2024-04-01, 20d
    
    section Observability
    OTEL Integration              :done, obs1, 2024-05-01, 30d
    Semantic Conventions          :done, obs2, after obs1, 25d
    Gap Analysis Tools            :done, obs3, after obs2, 20d
    Real-time Monitoring          :done, obs4, after obs3, 15d
    
    section v3 Consolidation
    Architecture Review           :active, v3-1, 2024-06-20, 10d
    Feature Consolidation         :v3-2, after v3-1, 15d
    Documentation Update          :v3-3, after v3-1, 20d
    Performance Optimization      :v3-4, after v3-2, 15d
    Release Preparation           :v3-5, after v3-4, 10d
"""
        
        self.mermaid_diagrams['timeline'] = mermaid
        return mermaid
    
    def generate_api_surface_mermaid(self) -> str:
        """Generate API surface diagram"""
        console.print("[cyan]🔌 Generating API surface diagram...[/cyan]")
        
        mermaid = """classDiagram
    class DSLModel {
        +from_prompt(prompt: str) DSLModel
        +from_template(template: str) DSLModel
        +from_signature(signature: str) DSLModel
        +to_yaml() str
        +to_json() str
        +save(path: Path) None
        +load(path: Path) DSLModel
        +validate() ValidationResult
        +render() str
    }
    
    class JinjaDSLMixin {
        +render_field(field: str) str
        +render_all() dict
        +get_template_vars() dict
    }
    
    class DSPyDSLMixin {
        +generate(prompt: str) dict
        +optimize(examples: list) None
        +predict(input: dict) dict
    }
    
    class FileHandlerDSLMixin {
        +to_yaml() str
        +to_json() str
        +to_toml() str
        +from_yaml(data: str) DSLModel
        +detect_format(path: Path) str
    }
    
    class FSMMixin {
        +add_state(state: str) None
        +add_transition(trigger: str) None
        +trigger(event: str) bool
        +get_state() str
        +get_transitions() list
    }
    
    class Workflow {
        +name: str
        +jobs: List[Job]
        +execute() WorkflowResult
        +validate() ValidationResult
        +get_dag() dict
    }
    
    class Job {
        +name: str
        +actions: List[Action]
        +dependencies: List[str]
        +execute() JobResult
    }
    
    class Action {
        +name: str
        +module: str
        +method: str
        +execute() ActionResult
    }
    
    DSLModel --|> JinjaDSLMixin
    DSLModel --|> DSPyDSLMixin
    DSLModel --|> FileHandlerDSLMixin
    DSLModel --|> FSMMixin
    
    Workflow "1" --> "*" Job
    Job "1" --> "*" Action
"""
        
        self.mermaid_diagrams['api_surface'] = mermaid
        return mermaid
    
    def display_component_stats(self):
        """Display component statistics"""
        console.print("\n[bold cyan]📊 Project Component Statistics[/bold cyan]")
        
        # Group by type
        by_type = defaultdict(list)
        for component in self.components.values():
            by_type[component.type].append(component)
        
        # Create stats table
        stats_table = Table(title="Component Analysis")
        stats_table.add_column("Type", style="cyan")
        stats_table.add_column("Count", style="yellow")
        stats_table.add_column("Total LOC", style="green")
        stats_table.add_column("Avg Complexity", style="red")
        stats_table.add_column("Key Components", style="blue")
        
        for comp_type, components in sorted(by_type.items()):
            total_loc = sum(c.lines_of_code for c in components)
            avg_complexity = sum(c.complexity for c in components) / len(components) if components else 0
            key_components = ", ".join(c.name for c in sorted(components, key=lambda x: x.lines_of_code, reverse=True)[:3])
            
            stats_table.add_row(
                comp_type.title(),
                str(len(components)),
                str(total_loc),
                f"{avg_complexity:.1f}",
                key_components
            )
        
        console.print(stats_table)
        
        # Feature summary
        all_features = []
        for component in self.components.values():
            all_features.extend(component.features)
        
        console.print(f"\n[green]Total Features: {len(all_features)}[/green]")
        console.print(f"[green]Total Lines of Code: {sum(c.lines_of_code for c in self.components.values())}[/green]")
    
    def display_visualization_tree(self):
        """Display project structure as a tree"""
        console.print("\n[bold cyan]🌳 Project Structure Tree[/bold cyan]")
        
        tree = Tree("DSLModel Project")
        
        # Core
        core_branch = tree.add("Core Components")
        for comp in sorted(self.components.values(), key=lambda x: x.name):
            if comp.type == "core":
                core_branch.add(f"{comp.name} ({comp.lines_of_code} LOC)")
        
        # Mixins
        mixin_branch = tree.add("Mixins")
        for comp in sorted(self.components.values(), key=lambda x: x.name):
            if comp.type == "mixin":
                mixin_branch.add(f"{comp.name} ({comp.lines_of_code} LOC)")
        
        # Examples
        example_branch = tree.add("Examples")
        for comp in sorted(self.components.values(), key=lambda x: x.name):
            if comp.type == "example":
                example_branch.add(f"{comp.name}")
        
        # Utilities
        util_branch = tree.add("Utilities")
        for comp in sorted(self.components.values(), key=lambda x: x.name):
            if comp.type == "utility":
                util_branch.add(f"{comp.name}")
        
        console.print(tree)
    
    def generate_all_visualizations(self) -> Dict[str, str]:
        """Generate all visualization diagrams"""
        console.print("[bold green]🎨 Generating all project visualizations...[/bold green]")
        
        # Analyze project first
        self.analyze_project()
        
        # Generate all diagrams
        diagrams = {
            'architecture': self.generate_architecture_mermaid(),
            'dependencies': self.generate_dependency_mermaid(),
            'feature_map': self.generate_feature_map_mermaid(),
            'data_flow': self.generate_data_flow_mermaid(),
            'timeline': self.generate_evolution_timeline_mermaid(),
            'api_surface': self.generate_api_surface_mermaid()
        }
        
        # Display stats
        self.display_component_stats()
        self.display_visualization_tree()
        
        return diagrams
    
    def save_visualizations(self, output_dir: Path):
        """Save all visualizations to files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Mermaid diagrams
        for name, diagram in self.mermaid_diagrams.items():
            file_path = output_dir / f"{name}_diagram.mmd"
            file_path.write_text(diagram)
            console.print(f"[green]✅ Saved {name} diagram to {file_path}[/green]")
        
        # Save component analysis
        analysis = {
            "components": {
                name: {
                    "type": comp.type,
                    "path": str(comp.path),
                    "imports": list(comp.imports),
                    "exports": list(comp.exports),
                    "dependencies": list(comp.dependencies),
                    "features": comp.features,
                    "complexity": comp.complexity,
                    "lines_of_code": comp.lines_of_code
                }
                for name, comp in self.components.items()
            },
            "statistics": {
                "total_components": len(self.components),
                "total_loc": sum(c.lines_of_code for c in self.components.values()),
                "total_features": sum(len(c.features) for c in self.components.values()),
                "by_type": {
                    comp_type: len([c for c in self.components.values() if c.type == comp_type])
                    for comp_type in set(c.type for c in self.components.values())
                }
            }
        }
        
        analysis_path = output_dir / "project_analysis.json"
        analysis_path.write_text(json.dumps(analysis, indent=2))
        console.print(f"[green]✅ Saved project analysis to {analysis_path}[/green]")


@app.command()
def visualize(
    output_dir: Path = typer.Option(Path("project_visualizations"), "--output", "-o", help="Output directory for visualizations"),
    show_stats: bool = typer.Option(True, "--stats", help="Show component statistics")
):
    """Generate comprehensive project visualizations for v3 consolidation"""
    
    console.print("[bold green]🎨 DSLModel Project Visualizer[/bold green]")
    console.print("=" * 60)
    
    visualizer = ProjectVisualizer()
    
    # Generate all visualizations
    diagrams = visualizer.generate_all_visualizations()
    
    # Save to files
    visualizer.save_visualizations(output_dir)
    
    # Create HTML viewer
    create_html_viewer(output_dir, diagrams)
    
    console.print(f"\n[bold green]✅ Project visualizations complete![/bold green]")
    console.print(f"[green]📁 Output saved to: {output_dir}[/green]")
    console.print(f"[green]🌐 Open {output_dir}/index.html to view interactive diagrams[/green]")


def create_html_viewer(output_dir: Path, diagrams: Dict[str, str]):
    """Create an HTML viewer for all diagrams"""
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>DSLModel v3 Project Visualizations</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 18px;
        }
        .nav {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        .nav button {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            background: #007acc;
            color: white;
            cursor: pointer;
            transition: background 0.3s;
        }
        .nav button:hover {
            background: #005a9e;
        }
        .nav button.active {
            background: #005a9e;
        }
        .diagram-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .diagram {
            display: none;
            text-align: center;
        }
        .diagram.active {
            display: block;
        }
        .diagram h2 {
            color: #333;
            margin-bottom: 20px;
        }
        .mermaid {
            text-align: center;
        }
        .description {
            max-width: 800px;
            margin: 20px auto;
            color: #666;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>DSLModel v3 Project Visualizations</h1>
        <p class="subtitle">Comprehensive project structure and architecture diagrams</p>
    </div>
    
    <div class="nav">
        <button onclick="showDiagram('architecture')" class="active">Architecture</button>
        <button onclick="showDiagram('dependencies')">Dependencies</button>
        <button onclick="showDiagram('feature_map')">Feature Map</button>
        <button onclick="showDiagram('data_flow')">Data Flow</button>
        <button onclick="showDiagram('timeline')">Timeline</button>
        <button onclick="showDiagram('api_surface')">API Surface</button>
    </div>
    
    <div class="diagram-container">
        <div id="architecture" class="diagram active">
            <h2>Architecture Overview</h2>
            <p class="description">
                High-level component architecture showing the relationships between core components,
                mixins, AI integration, examples, and infrastructure.
            </p>
            <div class="mermaid">
""" + diagrams['architecture'] + """
            </div>
        </div>
        
        <div id="dependencies" class="diagram">
            <h2>Dependency Graph</h2>
            <p class="description">
                Module dependency relationships showing how components interact and depend on each other.
            </p>
            <div class="mermaid">
""" + diagrams['dependencies'] + """
            </div>
        </div>
        
        <div id="feature_map" class="diagram">
            <h2>Feature Map</h2>
            <p class="description">
                Comprehensive mind map of all DSLModel features and capabilities organized by category.
            </p>
            <div class="mermaid">
""" + diagrams['feature_map'] + """
            </div>
        </div>
        
        <div id="data_flow" class="diagram">
            <h2>Data Flow</h2>
            <p class="description">
                Sequence diagram showing how data flows through the system during model creation and workflow execution.
            </p>
            <div class="mermaid">
""" + diagrams['data_flow'] + """
            </div>
        </div>
        
        <div id="timeline" class="diagram">
            <h2>Evolution Timeline</h2>
            <p class="description">
                Project evolution timeline showing development phases from initial creation to v3 consolidation.
            </p>
            <div class="mermaid">
""" + diagrams['timeline'] + """
            </div>
        </div>
        
        <div id="api_surface" class="diagram">
            <h2>API Surface</h2>
            <p class="description">
                Class diagram showing the public API surface of core DSLModel components and their methods.
            </p>
            <div class="mermaid">
""" + diagrams['api_surface'] + """
            </div>
        </div>
    </div>
    
    <script>
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {
                primaryColor: '#e1f5fe',
                primaryBorderColor: '#01579b',
                primaryTextColor: '#000',
                fontFamily: 'Arial, sans-serif'
            }
        });
        
        function showDiagram(diagramId) {
            // Hide all diagrams
            document.querySelectorAll('.diagram').forEach(d => d.classList.remove('active'));
            document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
            
            // Show selected diagram
            document.getElementById(diagramId).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>"""
    
    html_path = output_dir / "index.html"
    html_path.write_text(html_content)
    console.print(f"[green]✅ Created HTML viewer at {html_path}[/green]")


if __name__ == "__main__":
    app()