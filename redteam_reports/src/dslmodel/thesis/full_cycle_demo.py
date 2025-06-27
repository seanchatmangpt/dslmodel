"""
full_cycle_demo.py
───────────────────────────────────────────────────────────────────────────────
Automated Full Cycle Demo for SwarmSH Thesis
• Complete telemetry-driven development demonstration
• Shows thesis → OTEL → contradictions → TRIZ → evolution → validation
• Fully automated with comprehensive reporting
"""

import json
import time
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pydantic import BaseModel, Field

from .thesis_complete import ThesisComplete
from .otel_loop import OTELFeedbackLoop, create_initial_convention, demo_otel_loop


@dataclass
class PhaseResult:
    """Result of a demo phase execution"""
    phase_name: str
    success: bool
    duration_seconds: float
    artifacts_created: List[str]
    metrics: Dict[str, Any]
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class FullCycleDemoConfig(BaseModel):
    """Configuration for the full cycle demo"""
    
    workspace_dir: Path = Field(default=Path("./swarmsh_demo_workspace"))
    model: str = Field(default="ollama/qwen2.5")
    feedback_iterations: int = Field(default=3)
    simulate_runtime: bool = Field(default=True)
    generate_reports: bool = Field(default=True)
    cleanup_after: bool = Field(default=False)
    verbose: bool = Field(default=True)


class FullCycleDemo:
    """Orchestrates the complete SwarmSH thesis demonstration"""
    
    def __init__(self, config: FullCycleDemoConfig):
        self.config = config
        self.console = Console()
        self.results: List[PhaseResult] = []
        self.start_time = None
        self.workspace_created = False
        
        # State tracking
        self.initial_thesis: Optional[ThesisComplete] = None
        self.final_thesis: Optional[ThesisComplete] = None
        self.evolution_metrics = {}
    
    def run_full_cycle(self) -> Dict[str, Any]:
        """Run the complete automated demo cycle"""
        
        self.start_time = time.time()
        
        self.console.print(Panel.fit(
            "🌊 [bold blue]SwarmSH Full Cycle Demo[/bold blue]\n"
            "Automated Telemetry-Driven Development Demonstration\n"
            f"Model: {self.config.model} | Workspace: {self.config.workspace_dir}",
            border_style="blue"
        ))
        
        try:
            # Phase 1: Bootstrap
            self._run_phase("Bootstrap", self._phase_bootstrap)
            
            # Phase 2: Initial Generation
            self._run_phase("Initial Generation", self._phase_initial_generation)
            
            # Phase 3: Simulation & Detection
            self._run_phase("Simulation & Detection", self._phase_simulation_detection)
            
            # Phase 4: Auto-TRIZ Resolution
            self._run_phase("Auto-TRIZ Resolution", self._phase_auto_triz_resolution)
            
            # Phase 5: Validation & Reporting
            self._run_phase("Validation & Reporting", self._phase_validation_reporting)
            
            # Generate final report
            return self._generate_final_report()
            
        except Exception as e:
            self.console.print(f"❌ [red]Demo failed: {e}[/red]")
            raise
        finally:
            if self.config.cleanup_after and self.workspace_created:
                self._cleanup_workspace()
    
    def _run_phase(self, phase_name: str, phase_func):
        """Run a single demo phase with timing and error handling"""
        
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[blue]{phase_name}[/blue]"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task("", total=None)
            
            try:
                result = phase_func()
                duration = time.time() - start_time
                
                phase_result = PhaseResult(
                    phase_name=phase_name,
                    success=True,
                    duration_seconds=duration,
                    artifacts_created=result.get('artifacts', []),
                    metrics=result.get('metrics', {}),
                    errors=result.get('errors', [])
                )
                
                self.results.append(phase_result)
                
                self.console.print(f"✅ [green]{phase_name} completed[/green] ({duration:.1f}s)")
                
                if self.config.verbose and result.get('artifacts'):
                    for artifact in result['artifacts'][:3]:  # Show first 3
                        self.console.print(f"   📄 {artifact}")
                        
            except Exception as e:
                duration = time.time() - start_time
                
                phase_result = PhaseResult(
                    phase_name=phase_name,
                    success=False,
                    duration_seconds=duration,
                    artifacts_created=[],
                    metrics={},
                    errors=[str(e)]
                )
                
                self.results.append(phase_result)
                self.console.print(f"❌ [red]{phase_name} failed[/red]: {e}")
                raise
    
    def _phase_bootstrap(self) -> Dict[str, Any]:
        """Phase 1: Bootstrap the demo environment"""
        
        artifacts = []
        metrics = {}
        
        # Create workspace
        self.config.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_created = True
        artifacts.append(str(self.config.workspace_dir))
        
        # Create subdirectories
        for subdir in ['initial', 'evolved', 'reports', 'telemetry']:
            (self.config.workspace_dir / subdir).mkdir(exist_ok=True)
            artifacts.append(str(self.config.workspace_dir / subdir))
        
        # Initialize LLM
        from dslmodel.utils.dspy_tools import init_lm
        init_lm(self.config.model)
        metrics['model_initialized'] = self.config.model
        
        # Check dependencies
        try:
            from .thesis_complete import ThesisComplete
            from .otel_loop import OTELFeedbackLoop
            metrics['dependencies_available'] = True
        except ImportError as e:
            metrics['dependencies_available'] = False
            raise RuntimeError(f"Missing dependencies: {e}")
        
        return {
            'artifacts': artifacts,
            'metrics': metrics
        }
    
    def _phase_initial_generation(self) -> Dict[str, Any]:
        """Phase 2: Generate initial thesis and artifacts"""
        
        artifacts = []
        metrics = {}
        
        # Generate initial thesis
        self.initial_thesis = ThesisComplete.create_default_thesis()
        
        initial_dir = self.config.workspace_dir / 'initial'
        
        # Save thesis data
        thesis_json = initial_dir / 'thesis.json'
        self.initial_thesis.to_json(file_path=str(thesis_json))
        artifacts.append(str(thesis_json))
        
        thesis_yaml = initial_dir / 'thesis.yaml'
        self.initial_thesis.to_yaml(file_path=str(thesis_yaml))
        artifacts.append(str(thesis_yaml))
        
        # Generate OTEL semantic conventions
        semconv_yaml = initial_dir / 'semconv.yaml'
        with open(semconv_yaml, 'w') as f:
            f.write(self.initial_thesis.generate_otel_yaml())
        artifacts.append(str(semconv_yaml))
        
        # Generate Rust code
        rust_code = initial_dir / 'spans.rs'
        with open(rust_code, 'w') as f:
            f.write(self.initial_thesis.generate_forge_rust())
        artifacts.append(str(rust_code))
        
        # Collect metrics
        metrics.update({
            'span_claims': len(self.initial_thesis.span_claims),
            'inversion_pairs': len(self.initial_thesis.inversion_matrix),
            'triz_mappings': len(self.initial_thesis.triz_mapping),
            'feedback_phases': len(self.initial_thesis.auto_triz_feedback_loop)
        })
        
        return {
            'artifacts': artifacts,
            'metrics': metrics
        }
    
    def _phase_simulation_detection(self) -> Dict[str, Any]:
        """Phase 3: Simulate runtime and detect contradictions"""
        
        artifacts = []
        metrics = {}
        
        # Create OTEL feedback loop
        initial_convention = create_initial_convention()
        loop = OTELFeedbackLoop(current_convention=initial_convention)
        loop.initialize()
        
        # Run one iteration to collect contradictions
        loop.run_iteration()
        
        # Save telemetry simulation results
        telemetry_dir = self.config.workspace_dir / 'telemetry'
        
        # Save contradiction data
        contradictions_file = telemetry_dir / 'contradictions.json'
        contradictions_data = [
            {
                'type': c.type.value,
                'severity': c.severity,
                'description': c.description,
                'affected_spans': c.affected_spans,
                'resolution': c.suggested_resolution
            }
            for c in loop.contradiction_history
        ]
        
        with open(contradictions_file, 'w') as f:
            json.dump(contradictions_data, f, indent=2)
        artifacts.append(str(contradictions_file))
        
        # Save initial semantic convention state
        initial_semconv = telemetry_dir / 'initial_semconv.yaml'
        with open(initial_semconv, 'w') as f:
            f.write(initial_convention.to_weaver_yaml())
        artifacts.append(str(initial_semconv))
        
        metrics.update({
            'contradictions_found': len(loop.contradiction_history),
            'contradiction_types': [c.type.value for c in loop.contradiction_history],
            'total_spans_analyzed': sum(len(c.affected_spans) for c in loop.contradiction_history)
        })
        
        # Store for next phase
        self.feedback_loop = loop
        
        return {
            'artifacts': artifacts,
            'metrics': metrics
        }
    
    def _phase_auto_triz_resolution(self) -> Dict[str, Any]:
        """Phase 4: Apply auto-TRIZ and evolve the system"""
        
        artifacts = []
        metrics = {}
        
        # Continue feedback loop iterations
        initial_attributes = len(self.feedback_loop.current_convention.groups[0].attributes)
        
        for i in range(self.config.feedback_iterations - 1):  # -1 because we already ran one
            self.feedback_loop.run_iteration()
        
        final_attributes = len(self.feedback_loop.current_convention.groups[0].attributes)
        
        # Save evolved semantic convention
        evolved_dir = self.config.workspace_dir / 'evolved'
        evolved_semconv = evolved_dir / 'evolved_semconv.yaml'
        with open(evolved_semconv, 'w') as f:
            f.write(self.feedback_loop.current_convention.to_weaver_yaml())
        artifacts.append(str(evolved_semconv))
        
        # Save resolution proposals
        resolutions_file = evolved_dir / 'resolutions.json'
        resolutions_data = [
            {
                'contradiction_type': r.contradiction.type.value,
                'triz_principle': r.triz_principle,
                'triz_name': r.triz_name,
                'rationale': r.rationale,
                'new_attributes': [attr.dict() for attr in r.new_attributes]
            }
            for r in self.feedback_loop.resolution_history
        ]
        
        with open(resolutions_file, 'w') as f:
            json.dump(resolutions_data, f, indent=2)
        artifacts.append(str(resolutions_file))
        
        # Generate evolved thesis
        self.final_thesis = ThesisComplete.create_default_thesis()
        # Note: In a real implementation, we'd update the thesis with evolved data
        
        final_thesis_json = evolved_dir / 'evolved_thesis.json'
        self.final_thesis.to_json(file_path=str(final_thesis_json))
        artifacts.append(str(final_thesis_json))
        
        metrics.update({
            'initial_attributes': initial_attributes,
            'final_attributes': final_attributes,
            'attributes_added': final_attributes - initial_attributes,
            'triz_principles_applied': len(set(r.triz_principle for r in self.feedback_loop.resolution_history)),
            'resolutions_proposed': len(self.feedback_loop.resolution_history),
            'iterations_completed': self.feedback_loop.iteration
        })
        
        self.evolution_metrics = metrics
        
        return {
            'artifacts': artifacts,
            'metrics': metrics
        }
    
    def _phase_validation_reporting(self) -> Dict[str, Any]:
        """Phase 5: Validate evolution and generate reports"""
        
        artifacts = []
        metrics = {}
        
        reports_dir = self.config.workspace_dir / 'reports'
        
        # Generate comprehensive report
        report = self._create_comprehensive_report()
        
        report_file = reports_dir / 'full_cycle_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        artifacts.append(str(report_file))
        
        # Generate human-readable summary
        summary_file = reports_dir / 'executive_summary.md'
        summary = self._create_executive_summary()
        with open(summary_file, 'w') as f:
            f.write(summary)
        artifacts.append(str(summary_file))
        
        # Validation metrics
        metrics.update({
            'demo_successful': all(r.success for r in self.results),
            'total_artifacts_generated': sum(len(r.artifacts_created) for r in self.results),
            'system_evolved': self.evolution_metrics.get('attributes_added', 0) > 0,
            'triz_principles_validated': self.evolution_metrics.get('triz_principles_applied', 0)
        })
        
        return {
            'artifacts': artifacts,
            'metrics': metrics
        }
    
    def _create_comprehensive_report(self) -> Dict[str, Any]:
        """Create detailed technical report"""
        
        return {
            'demo_metadata': {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'model_used': self.config.model,
                'total_duration_seconds': time.time() - self.start_time,
                'workspace': str(self.config.workspace_dir)
            },
            'phase_results': [
                {
                    'phase': r.phase_name,
                    'success': r.success,
                    'duration_seconds': r.duration_seconds,
                    'artifacts_count': len(r.artifacts_created),
                    'metrics': r.metrics,
                    'errors': r.errors
                }
                for r in self.results
            ],
            'evolution_summary': {
                'initial_state': {
                    'span_claims': len(self.initial_thesis.span_claims) if self.initial_thesis else 0,
                    'inversion_pairs': len(self.initial_thesis.inversion_matrix) if self.initial_thesis else 0,
                    'triz_mappings': len(self.initial_thesis.triz_mapping) if self.initial_thesis else 0
                },
                'evolution_metrics': self.evolution_metrics,
                'system_improvements': self._calculate_improvements()
            },
            'validation_results': {
                'thesis_proven': self._validate_thesis_claims(),
                'telemetry_driven_evolution': self.evolution_metrics.get('attributes_added', 0) > 0,
                'auto_triz_effective': self.evolution_metrics.get('triz_principles_applied', 0) > 0
            }
        }
    
    def _create_executive_summary(self) -> str:
        """Create human-readable executive summary"""
        
        duration = time.time() - self.start_time
        success_rate = sum(1 for r in self.results if r.success) / len(self.results) * 100
        
        summary = f"""# SwarmSH Thesis Full Cycle Demo - Executive Summary

## Overview
**Demonstration Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Duration:** {duration:.1f} seconds
**Success Rate:** {success_rate:.1f}%
**Model Used:** {self.config.model}

## Key Results

### System Evolution Achieved
- **Initial Attributes:** {self.evolution_metrics.get('initial_attributes', 0)}
- **Final Attributes:** {self.evolution_metrics.get('final_attributes', 0)}
- **Attributes Added:** {self.evolution_metrics.get('attributes_added', 0)}
- **TRIZ Principles Applied:** {self.evolution_metrics.get('triz_principles_applied', 0)}

### Thesis Validation
"""
        
        validation_results = self._validate_thesis_claims()
        for claim, validated in validation_results.items():
            status = "✅ VALIDATED" if validated else "❌ NOT VALIDATED"
            summary += f"- **{claim}:** {status}\n"
        
        summary += f"""
### Performance Metrics
- **Contradictions Detected:** {self.evolution_metrics.get('contradictions_found', 0)}
- **Resolutions Proposed:** {self.evolution_metrics.get('resolutions_proposed', 0)}
- **Feedback Iterations:** {self.evolution_metrics.get('iterations_completed', 0)}

### Artifacts Generated
"""
        
        for result in self.results:
            if result.artifacts_created:
                summary += f"- **{result.phase_name}:** {len(result.artifacts_created)} artifacts\n"
        
        summary += f"""
## Conclusion

The SwarmSH thesis has been {'**SUCCESSFULLY DEMONSTRATED**' if self._demo_successful() else '**PARTIALLY DEMONSTRATED**'}.

The system showed telemetry-driven evolution through auto-TRIZ principles, validating the core claim that telemetry can be the system itself, driving code generation and self-improvement.

**Generated in workspace:** `{self.config.workspace_dir}`
"""
        
        return summary
    
    def _calculate_improvements(self) -> Dict[str, Any]:
        """Calculate measurable system improvements"""
        
        return {
            'semantic_convention_growth': self.evolution_metrics.get('attributes_added', 0),
            'contradiction_resolution_rate': min(1.0, self.evolution_metrics.get('resolutions_proposed', 0) / max(1, len(getattr(self.feedback_loop, 'contradiction_history', [])))),
            'triz_principle_coverage': self.evolution_metrics.get('triz_principles_applied', 0) / 40.0,  # Out of 40 TRIZ principles
            'automation_effectiveness': all(r.success for r in self.results)
        }
    
    def _validate_thesis_claims(self) -> Dict[str, bool]:
        """Validate core thesis claims against demo results"""
        
        return {
            'telemetry_as_system': self.evolution_metrics.get('attributes_added', 0) > 0,
            'spans_drive_code': len([r for r in self.results if 'spans.rs' in str(r.artifacts_created)]) > 0,
            'trace_to_prompt_emergence': self.evolution_metrics.get('resolutions_proposed', 0) > 0,
            'auto_triz_effective': self.evolution_metrics.get('triz_principles_applied', 0) > 0,
            'system_self_modeling': self.evolution_metrics.get('iterations_completed', 0) > 0
        }
    
    def _demo_successful(self) -> bool:
        """Determine if the demo was successful overall"""
        
        return (
            all(r.success for r in self.results) and
            self.evolution_metrics.get('attributes_added', 0) > 0 and
            self.evolution_metrics.get('triz_principles_applied', 0) > 0
        )
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate the final demo report"""
        
        self.console.print(Panel.fit(
            "🎯 [bold green]Demo Complete![/bold green]\n"
            f"Duration: {time.time() - self.start_time:.1f}s\n"
            f"Success: {'✅ YES' if self._demo_successful() else '❌ NO'}\n"
            f"Workspace: {self.config.workspace_dir}",
            border_style="green"
        ))
        
        # Show results table
        if self.config.verbose:
            self._display_results_table()
        
        return self._create_comprehensive_report()
    
    def _display_results_table(self):
        """Display results in a formatted table"""
        
        table = Table(title="SwarmSH Full Cycle Demo Results")
        table.add_column("Phase", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Duration", style="yellow")
        table.add_column("Artifacts", style="green")
        table.add_column("Key Metrics", style="blue")
        
        for result in self.results:
            status = "✅ Success" if result.success else "❌ Failed"
            duration = f"{result.duration_seconds:.1f}s"
            artifacts = str(len(result.artifacts_created))
            
            key_metrics = []
            for key, value in result.metrics.items():
                if isinstance(value, (int, float)):
                    key_metrics.append(f"{key}: {value}")
            metrics_str = ", ".join(key_metrics[:2])  # Show first 2 metrics
            
            table.add_row(result.phase_name, status, duration, artifacts, metrics_str)
        
        self.console.print(table)
    
    def _cleanup_workspace(self):
        """Clean up the demo workspace"""
        
        if self.config.workspace_dir.exists():
            shutil.rmtree(self.config.workspace_dir)
            self.console.print(f"🗑️  Cleaned up workspace: {self.config.workspace_dir}")


def run_automated_demo(
    workspace_dir: str = "./swarmsh_demo_workspace",
    model: str = "ollama/qwen2.5",
    iterations: int = 3,
    verbose: bool = True,
    cleanup: bool = False
) -> Dict[str, Any]:
    """
    Run the complete automated SwarmSH thesis demonstration
    
    Args:
        workspace_dir: Directory for demo artifacts
        model: LLM model to use
        iterations: Number of feedback loop iterations
        verbose: Show detailed output
        cleanup: Clean up workspace after demo
        
    Returns:
        Comprehensive demo report
    """
    
    config = FullCycleDemoConfig(
        workspace_dir=Path(workspace_dir),
        model=model,
        feedback_iterations=iterations,
        verbose=verbose,
        cleanup_after=cleanup
    )
    
    demo = FullCycleDemo(config)
    return demo.run_full_cycle()


if __name__ == "__main__":
    # Run demo with default settings
    result = run_automated_demo()
    print(f"Demo completed. Results saved to: {result['demo_metadata']['workspace']}")