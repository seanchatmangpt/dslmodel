#!/usr/bin/env python3
"""
Agent Evolution System - Automatically evolves coordination patterns
Uses OTEL telemetry to identify optimization opportunities and generate new patterns
Built on weaver-first semantic conventions approach
"""

import os
import json
import yaml
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import subprocess

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import Status, StatusCode

@dataclass
class EvolutionPattern:
    """Discovered coordination pattern"""
    pattern_id: str
    span_sequence: List[str]
    frequency: int
    avg_duration_ms: float
    success_rate: float
    optimization_potential: float
    recommended_changes: List[str]

@dataclass
class PerformanceMetric:
    """Performance metric for coordination patterns"""
    metric_name: str
    current_value: float
    target_value: float
    improvement_percentage: float
    confidence: float

class AgentEvolutionSystem:
    """
    Evolves agent coordination patterns automatically using OTEL data
    Implements weaver-first approach for generated optimizations
    """
    
    def __init__(self, trace_data_path: str = "otel_traces", semantic_conventions_path: str = "semantic_conventions"):
        self.trace_data_path = Path(trace_data_path)
        self.semantic_conventions_path = Path(semantic_conventions_path)
        self.evolution_history: List[Dict[str, Any]] = []
        self.discovered_patterns: Dict[str, EvolutionPattern] = {}
        self.performance_baselines: Dict[str, float] = {}
        self.optimization_targets: Dict[str, float] = {}
        
        # Initialize telemetry for evolution system itself
        self.tracer = trace.get_tracer(__name__)
        
        # Pattern analysis thresholds
        self.min_pattern_frequency = 5
        self.min_success_rate = 0.8
        self.performance_improvement_threshold = 0.15
        
    def start_evolution_cycle(self) -> str:
        """Start new evolution cycle with telemetry"""
        cycle_id = f"evolution_{int(time.time())}"
        
        with self.tracer.start_as_current_span("evolution.cycle.start") as span:
            span.set_attribute("cycle.id", cycle_id)
            span.set_attribute("analysis.start_time", datetime.now().isoformat())
            
            try:
                # Analyze current telemetry data
                patterns = self._analyze_coordination_patterns()
                span.set_attribute("patterns.discovered", len(patterns))
                
                # Identify optimization opportunities
                optimizations = self._identify_optimizations(patterns)
                span.set_attribute("optimizations.identified", len(optimizations))
                
                # Generate evolved semantic conventions
                new_conventions = self._generate_evolved_conventions(optimizations)
                span.set_attribute("conventions.generated", len(new_conventions))
                
                # Apply evolution changes
                success = self._apply_evolution_changes(cycle_id, new_conventions)
                span.set_attribute("evolution.applied", success)
                
                span.set_status(Status(StatusCode.OK))
                return cycle_id
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def _analyze_coordination_patterns(self) -> List[EvolutionPattern]:
        """Analyze OTEL traces to discover coordination patterns"""
        patterns = []
        
        with self.tracer.start_as_current_span("evolution.analyze.patterns") as span:
            try:
                # Load trace data (simulated - in real implementation would read from OTEL backend)
                trace_sequences = self._load_trace_sequences()
                span.set_attribute("trace_sequences.loaded", len(trace_sequences))
                
                # Group by coordination sequence
                sequence_groups = defaultdict(list)
                for seq in trace_sequences:
                    sequence_key = "->".join(seq["span_names"])
                    sequence_groups[sequence_key].append(seq)
                
                # Analyze each pattern
                for sequence_key, sequences in sequence_groups.items():
                    if len(sequences) >= self.min_pattern_frequency:
                        pattern = self._analyze_pattern_performance(sequence_key, sequences)
                        if pattern:
                            patterns.append(pattern)
                
                span.set_attribute("patterns.analyzed", len(patterns))
                span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
        
        return patterns
    
    def _analyze_pattern_performance(self, sequence_key: str, sequences: List[Dict]) -> Optional[EvolutionPattern]:
        """Analyze performance of a specific coordination pattern"""
        
        # Calculate metrics
        total_duration = sum(seq["total_duration_ms"] for seq in sequences)
        avg_duration = total_duration / len(sequences)
        
        successful_sequences = [seq for seq in sequences if seq["success"]]
        success_rate = len(successful_sequences) / len(sequences)
        
        # Skip patterns with low success rate
        if success_rate < self.min_success_rate:
            return None
        
        # Calculate optimization potential based on duration variance
        durations = [seq["total_duration_ms"] for seq in sequences]
        duration_variance = self._calculate_variance(durations)
        optimization_potential = min(duration_variance / avg_duration, 1.0)
        
        # Generate recommendations
        recommendations = self._generate_pattern_recommendations(sequence_key, sequences)
        
        pattern_id = f"pattern_{hash(sequence_key) % 10000:04d}"
        
        return EvolutionPattern(
            pattern_id=pattern_id,
            span_sequence=sequence_key.split("->"),
            frequency=len(sequences),
            avg_duration_ms=avg_duration,
            success_rate=success_rate,
            optimization_potential=optimization_potential,
            recommended_changes=recommendations
        )
    
    def _generate_pattern_recommendations(self, sequence_key: str, sequences: List[Dict]) -> List[str]:
        """Generate optimization recommendations for a pattern"""
        recommendations = []
        
        # Analyze timing patterns
        avg_duration = sum(seq["total_duration_ms"] for seq in sequences) / len(sequences)
        
        # Parallel execution recommendation
        if "agent.coordination.request->agent.coordination.response" in sequence_key:
            if avg_duration > 1000:  # More than 1 second
                recommendations.append("parallel_coordination")
        
        # Caching recommendation
        if sequence_key.count("agent.worktree.create") > 1:
            recommendations.append("worktree_pooling")
        
        # Batch processing recommendation
        if sequence_key.count("agent.task.progress") > 5:
            recommendations.append("batch_progress_updates")
        
        # Preemptive coordination
        frequent_coord_patterns = [seq for seq in sequences if "coordination" in str(seq["span_names"])]
        if len(frequent_coord_patterns) > len(sequences) * 0.8:
            recommendations.append("preemptive_coordination")
        
        return recommendations
    
    def _identify_optimizations(self, patterns: List[EvolutionPattern]) -> List[Dict[str, Any]]:
        """Identify specific optimizations based on discovered patterns"""
        optimizations = []
        
        with self.tracer.start_as_current_span("evolution.identify.optimizations") as span:
            
            for pattern in patterns:
                # High optimization potential patterns
                if pattern.optimization_potential > self.performance_improvement_threshold:
                    
                    for recommendation in pattern.recommended_changes:
                        optimization = {
                            "type": recommendation,
                            "pattern_id": pattern.pattern_id,
                            "current_performance": pattern.avg_duration_ms,
                            "expected_improvement": pattern.optimization_potential,
                            "span_sequence": pattern.span_sequence,
                            "implementation": self._get_optimization_implementation(recommendation)
                        }
                        optimizations.append(optimization)
            
            span.set_attribute("optimizations.count", len(optimizations))
        
        return optimizations
    
    def _get_optimization_implementation(self, recommendation_type: str) -> Dict[str, Any]:
        """Get implementation details for optimization type"""
        implementations = {
            "parallel_coordination": {
                "new_spans": ["agent.coordination.parallel_request", "agent.coordination.parallel_response"],
                "attribute_changes": {"coordination.mode": "parallel"},
                "pipeline_changes": ["async_coordination_handler"]
            },
            "worktree_pooling": {
                "new_spans": ["agent.worktree.pool_get", "agent.worktree.pool_return"],
                "attribute_changes": {"worktree.pooled": True, "worktree.pool_id": "string"},
                "pipeline_changes": ["worktree_pool_manager"]
            },
            "batch_progress_updates": {
                "new_spans": ["agent.task.progress_batch"],
                "attribute_changes": {"progress.batch_size": "int", "progress.batch_interval_ms": "float"},
                "pipeline_changes": ["progress_batch_collector"]
            },
            "preemptive_coordination": {
                "new_spans": ["agent.coordination.preemptive_setup", "agent.coordination.preemptive_execute"],
                "attribute_changes": {"coordination.preemptive": True, "coordination.prediction_confidence": "float"},
                "pipeline_changes": ["coordination_predictor"]
            }
        }
        
        return implementations.get(recommendation_type, {})
    
    def _generate_evolved_conventions(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate new semantic conventions based on optimizations"""
        
        with self.tracer.start_as_current_span("evolution.generate.conventions") as span:
            
            # Load existing conventions
            base_conventions = self._load_base_conventions()
            
            # Create evolved version
            evolved_conventions = {
                "groups": base_conventions.get("groups", []).copy(),
                "semantic_convention_version": "2.0.0",
                "evolution_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "optimizations_applied": len(optimizations),
                    "base_version": "1.0.0"
                }
            }
            
            # Add new spans based on optimizations
            for optimization in optimizations:
                implementation = optimization["implementation"]
                
                for new_span in implementation.get("new_spans", []):
                    span_def = self._create_span_definition(new_span, optimization)
                    evolved_conventions["groups"].append(span_def)
                
                # Update existing spans with new attributes
                self._update_existing_spans(evolved_conventions, optimization)
            
            span.set_attribute("conventions.spans_added", 
                             sum(len(opt["implementation"].get("new_spans", [])) for opt in optimizations))
            
        return evolved_conventions
    
    def _create_span_definition(self, span_name: str, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Create semantic convention definition for new span"""
        
        # Parse span name to determine type and category
        parts = span_name.split(".")
        category = parts[0] if len(parts) > 0 else "agent"
        operation = ".".join(parts[1:]) if len(parts) > 1 else "operation"
        
        base_attributes = [
            {"id": "agent.id", "type": "string", "brief": "Unique identifier for the agent", "requirement_level": "required"},
            {"id": "operation.duration_ms", "type": "double", "brief": "Duration of operation in milliseconds", "requirement_level": "recommended"}
        ]
        
        # Add optimization-specific attributes
        implementation = optimization["implementation"]
        for attr_name, attr_type in implementation.get("attribute_changes", {}).items():
            base_attributes.append({
                "id": attr_name,
                "type": attr_type,
                "brief": f"Optimization attribute for {optimization['type']}",
                "requirement_level": "recommended"
            })
        
        return {
            "id": span_name,
            "type": "span",
            "brief": f"Evolved {operation} operation for {optimization['type']} optimization",
            "attributes": base_attributes,
            "events": [],
            "span_kind": "internal",
            "stability": "experimental"
        }
    
    def _update_existing_spans(self, conventions: Dict[str, Any], optimization: Dict[str, Any]):
        """Update existing span definitions with new attributes"""
        implementation = optimization["implementation"]
        attribute_changes = implementation.get("attribute_changes", {})
        
        if not attribute_changes:
            return
        
        # Find spans in the optimization pattern and update them
        pattern_spans = set(optimization["span_sequence"])
        
        for group in conventions["groups"]:
            if group.get("id") in pattern_spans:
                existing_attrs = group.get("attributes", [])
                existing_attr_ids = {attr["id"] for attr in existing_attrs}
                
                # Add new attributes
                for attr_name, attr_type in attribute_changes.items():
                    if attr_name not in existing_attr_ids:
                        existing_attrs.append({
                            "id": attr_name,
                            "type": attr_type,
                            "brief": f"Evolution optimization attribute",
                            "requirement_level": "recommended"
                        })
    
    def _apply_evolution_changes(self, cycle_id: str, new_conventions: Dict[str, Any]) -> bool:
        """Apply evolved conventions and generate new code"""
        
        with self.tracer.start_as_current_span("evolution.apply.changes") as span:
            span.set_attribute("cycle.id", cycle_id)
            
            try:
                # Save evolved conventions
                evolved_file = self.semantic_conventions_path / f"worktree_pipeline_evolved_{cycle_id}.yaml"
                with open(evolved_file, 'w') as f:
                    yaml.dump(new_conventions, f, default_flow_style=False)
                
                span.set_attribute("conventions.saved", str(evolved_file))
                
                # Generate evolved models using weaver
                success = self._generate_evolved_models(evolved_file, cycle_id)
                span.set_attribute("models.generated", success)
                
                # Update pipeline with new capabilities
                if success:
                    pipeline_success = self._update_pipeline_with_evolution(cycle_id, new_conventions)
                    span.set_attribute("pipeline.updated", pipeline_success)
                    
                    # Record evolution in history
                    self._record_evolution_cycle(cycle_id, new_conventions)
                    
                    return pipeline_success
                
                return False
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                return False
    
    def _generate_evolved_models(self, conventions_file: Path, cycle_id: str) -> bool:
        """Generate evolved models using weaver"""
        try:
            # Use weaver to generate evolved models
            output_dir = Path(f"src/dslmodel/agents/generated/evolved_{cycle_id}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run weaver generation (would use actual weaver command)
            # For now, create evolved models manually based on conventions
            evolved_models_content = self._create_evolved_models_content(conventions_file, cycle_id)
            
            evolved_models_file = output_dir / "worktree_models.py"
            with open(evolved_models_file, 'w') as f:
                f.write(evolved_models_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to generate evolved models: {e}")
            return False
    
    def _create_evolved_models_content(self, conventions_file: Path, cycle_id: str) -> str:
        """Create evolved models content based on new conventions"""
        
        # Load the evolved conventions
        with open(conventions_file, 'r') as f:
            conventions = yaml.safe_load(f)
        
        # Generate Python code for evolved models
        content = f'''#!/usr/bin/env python3
"""
Evolved Agent Worktree Models - Cycle {cycle_id}
Auto-generated from evolved semantic conventions
Generated at: {datetime.now().isoformat()}
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Import base models
from ..worktree_models import *

# Evolution metadata
EVOLUTION_CYCLE = "{cycle_id}"
EVOLUTION_VERSION = "{conventions.get('semantic_convention_version', '2.0.0')}"
OPTIMIZATIONS_APPLIED = {len(conventions.get('evolution_metadata', {}).get('optimizations_applied', 0))}

'''
        
        # Add new span classes based on evolved conventions
        for group in conventions.get("groups", []):
            if group.get("stability") == "experimental":  # Only new spans
                content += self._generate_evolved_span_class(group)
        
        # Add evolved factory
        content += '''
class EvolvedWorktreeSpanFactory(WorktreeSpanFactory):
    """Evolved factory with optimization capabilities"""
    
    _evolved_span_classes = {
'''
        
        # Add evolved spans to factory
        for group in conventions.get("groups", []):
            if group.get("stability") == "experimental":
                span_name = group.get("id", "")
                class_name = self._span_name_to_class_name(span_name)
                content += f'        "{span_name}": {class_name},\n'
        
        content += '''    }
    
    @classmethod
    def create_evolved_span(cls, span_name: str, **attributes) -> Any:
        """Create evolved span instance"""
        if span_name in cls._evolved_span_classes:
            span_class = cls._evolved_span_classes[span_name]
            return span_class.from_attributes(**attributes)
        else:
            # Fallback to base factory
            return super().create_span(span_name, **attributes)
'''
        
        return content
    
    def _generate_evolved_span_class(self, span_def: Dict[str, Any]) -> str:
        """Generate Python class for evolved span"""
        span_name = span_def.get("id", "")
        class_name = self._span_name_to_class_name(span_name)
        brief = span_def.get("brief", "")
        attributes = span_def.get("attributes", [])
        
        content = f'''
@dataclass
class {class_name}:
    """{brief}"""
    
    # Span attributes
'''
        
        # Add attributes
        for attr in attributes:
            attr_name = attr["id"].replace(".", "_")
            attr_type = self._convert_type(attr["type"])
            is_required = attr.get("requirement_level") == "required"
            
            if is_required:
                content += f'    {attr_name}: {attr_type}\n'
            else:
                content += f'    {attr_name}: {attr_type} = None\n'
        
        # Add standard methods
        content += f'''
    # Span metadata
    span_name: str = "{span_name}"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
'''
        
        for attr in attributes:
            attr_name = attr["id"].replace(".", "_")
            attr_id = attr["id"]
            content += f'''        if self.{attr_name} is not None:
            span.set_attribute("{attr_id}", self.{attr_name})
'''
        
        content += '''        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs):
        """Create span from attribute dictionary"""
        valid_attrs = {}
'''
        
        for attr in attributes:
            attr_name = attr["id"].replace(".", "_")
            content += f'''        if "{attr_name}" in kwargs:
            valid_attrs["{attr_name}"] = kwargs["{attr_name}"]
'''
        
        content += '''        return cls(**valid_attrs)
'''
        
        return content
    
    def _span_name_to_class_name(self, span_name: str) -> str:
        """Convert span name to Python class name"""
        parts = span_name.split(".")
        return "".join(word.capitalize() for word in parts) + "Span"
    
    def _convert_type(self, attr_type: str) -> str:
        """Convert semantic convention type to Python type"""
        type_map = {
            "string": "str",
            "int": "int", 
            "double": "float",
            "boolean": "bool",
            "string[]": "List[str]",
            "int[]": "List[int]"
        }
        return type_map.get(attr_type, "str")
    
    def _update_pipeline_with_evolution(self, cycle_id: str, conventions: Dict[str, Any]) -> bool:
        """Update pipeline to use evolved capabilities"""
        try:
            # Create evolved pipeline class that inherits from base
            evolved_pipeline_file = Path(f"src/dslmodel/agents/evolved_pipeline_{cycle_id}.py")
            
            pipeline_content = f'''#!/usr/bin/env python3
"""
Evolved Worktree Pipeline - Cycle {cycle_id}
Extends base pipeline with evolved coordination patterns
"""

from .worktree_pipeline import AgentWorktreePipeline
from .generated.evolved_{cycle_id}.worktree_models import EvolvedWorktreeSpanFactory

class EvolvedAgentWorktreePipeline(AgentWorktreePipeline):
    """Pipeline with evolved coordination capabilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.evolution_cycle = "{cycle_id}"
        self.span_factory = EvolvedWorktreeSpanFactory()
    
    # Add evolved coordination methods here based on optimizations
    async def parallel_coordination(self, requesting_agent: str, target_agents: List[str], reason: str):
        """Evolved parallel coordination capability"""
        # Implementation would use evolved span models
        pass
    
    async def batch_progress_updates(self, agent_id: str, updates: List[Dict]):
        """Evolved batch progress update capability"""
        # Implementation would use evolved span models
        pass
'''
            
            with open(evolved_pipeline_file, 'w') as f:
                f.write(pipeline_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to update pipeline: {e}")
            return False
    
    def _record_evolution_cycle(self, cycle_id: str, conventions: Dict[str, Any]):
        """Record evolution cycle in history"""
        evolution_record = {
            "cycle_id": cycle_id,
            "timestamp": datetime.now().isoformat(),
            "optimizations": conventions.get("evolution_metadata", {}),
            "performance_improvements": self._calculate_performance_improvements(),
            "new_spans": [group["id"] for group in conventions.get("groups", []) 
                         if group.get("stability") == "experimental"]
        }
        
        self.evolution_history.append(evolution_record)
        
        # Save evolution history
        history_file = Path("evolution_history.json")
        with open(history_file, 'w') as f:
            json.dump(self.evolution_history, f, indent=2)
    
    def _calculate_performance_improvements(self) -> Dict[str, float]:
        """Calculate performance improvements from evolution"""
        # This would analyze before/after performance metrics
        # For now, return simulated improvements
        return {
            "avg_coordination_time_ms": -15.5,  # 15.5ms improvement
            "success_rate": 0.03,  # 3% improvement
            "resource_utilization": -0.08,  # 8% less resource usage
        }
    
    # Utility methods for data loading (simulated)
    def _load_trace_sequences(self) -> List[Dict[str, Any]]:
        """Load trace sequences from OTEL backend (simulated)"""
        # In real implementation, would query OTEL backend
        return [
            {
                "span_names": ["agent.worktree.create", "agent.worktree.activate", "agent.task.start"],
                "total_duration_ms": 1250.0,
                "success": True
            },
            {
                "span_names": ["agent.coordination.request", "agent.coordination.response"],
                "total_duration_ms": 850.0,
                "success": True
            },
            {
                "span_names": ["agent.task.progress", "agent.task.progress", "agent.task.complete"],
                "total_duration_ms": 2100.0,
                "success": True
            }
        ]
    
    def _load_base_conventions(self) -> Dict[str, Any]:
        """Load base semantic conventions"""
        base_file = self.semantic_conventions_path / "worktree_pipeline.yaml"
        if base_file.exists():
            with open(base_file, 'r') as f:
                return yaml.safe_load(f)
        return {"groups": []}
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

# Example usage
async def run_evolution_cycle():
    """Run a complete evolution cycle"""
    evolution_system = AgentEvolutionSystem()
    cycle_id = evolution_system.start_evolution_cycle()
    print(f"Evolution cycle {cycle_id} completed")
    return cycle_id

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evolution_cycle())