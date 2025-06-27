#!/usr/bin/env python3
"""
OTEL Learning Engine - Feed Telemetry Data to Language Models
Aggregates all OpenTelemetry data across the system and feeds it to init_lm
for the language model to learn from operational patterns.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import statistics
import uuid

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.tree import Tree
from loguru import logger

from ..utils.json_output import json_command
from ..utils.dspy_tools import init_lm

app = typer.Typer(help="OTEL Learning Engine - Feed telemetry to language models")
console = Console()


@dataclass
class OTELDataSource:
    """Represents a source of OTEL telemetry data"""
    path: Path
    data_type: str  # "coordination", "swarm", "validation", "claude_cognitive", "ecosystem"
    size_bytes: int = 0
    span_count: int = 0
    trace_count: int = 0
    last_modified: Optional[datetime] = None
    
    def __post_init__(self):
        if self.path.exists():
            stat = self.path.stat()
            self.size_bytes = stat.st_size
            self.last_modified = datetime.fromtimestamp(stat.st_mtime)


@dataclass
class OTELLearningSession:
    """Learning session for feeding OTEL data to language models"""
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    data_sources: List[OTELDataSource] = field(default_factory=list)
    aggregated_spans: List[Dict[str, Any]] = field(default_factory=list)
    aggregated_metrics: Dict[str, Any] = field(default_factory=dict)
    learned_patterns: Dict[str, Any] = field(default_factory=dict)
    model_insights: List[Dict[str, Any]] = field(default_factory=list)
    total_data_processed: int = 0
    

class OTELLearningEngine:
    """Advanced OTEL data aggregation and language model learning system"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.session = OTELLearningSession()
        self.console = console
        
    async def discover_otel_sources(self) -> List[OTELDataSource]:
        """Discover all OTEL telemetry data sources in the system"""
        
        sources = []
        
        # Define telemetry file patterns and their types
        telemetry_patterns = [
            ("**/telemetry*.json", "coordination"),
            ("**/swarm_data/telemetry.json", "swarm"),
            ("**/otel_concurrent_tests/telemetry_data.json", "validation"),
            ("**/otel_ecosystem_test_report.json", "ecosystem"),
            ("**/*telemetry*.json", "generic")
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Discovering OTEL sources...", total=len(telemetry_patterns))
            
            for pattern, data_type in telemetry_patterns:
                try:
                    # Search from base path
                    matching_files = list(self.base_path.rglob(pattern))
                    
                    for file_path in matching_files:
                        if file_path.exists() and file_path.suffix == '.json':
                            source = OTELDataSource(
                                path=file_path,
                                data_type=data_type
                            )
                            
                            # Analyze file content to determine span/trace counts
                            try:
                                with open(file_path, 'r') as f:
                                    data = json.load(f)
                                    
                                if isinstance(data, dict):
                                    if 'spans' in data:
                                        source.span_count = len(data['spans'])
                                    if 'traces' in data:
                                        source.trace_count = len(data['traces'])
                                    if 'test_results' in data:
                                        source.data_type = "ecosystem"
                                elif isinstance(data, list):
                                    source.span_count = len(data)
                                    
                            except Exception as e:
                                logger.warning(f"Could not analyze {file_path}: {e}")
                            
                            sources.append(source)
                            
                except Exception as e:
                    logger.warning(f"Error searching pattern {pattern}: {e}")
                
                progress.advance(task)
        
        # Remove duplicates and sort by data type and size
        unique_sources = {}
        for source in sources:
            key = str(source.path)
            if key not in unique_sources or source.span_count > unique_sources[key].span_count:
                unique_sources[key] = source
        
        sorted_sources = sorted(unique_sources.values(), 
                               key=lambda x: (x.data_type, -x.span_count))
        
        self.session.data_sources = sorted_sources
        return sorted_sources
    
    async def aggregate_telemetry_data(self) -> Dict[str, Any]:
        """Aggregate all telemetry data into comprehensive dataset"""
        
        aggregated_data = {
            'spans': [],
            'metrics': {},
            'patterns': {},
            'insights': {},
            'metadata': {
                'session_id': self.session.session_id,
                'sources_processed': 0,
                'total_spans': 0,
                'total_traces': 0,
                'aggregation_timestamp': datetime.utcnow().isoformat(),
                'data_types': {}
            }
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Aggregating telemetry data...", 
                                   total=len(self.session.data_sources))
            
            for source in self.session.data_sources:
                progress.update(task, description=f"Processing {source.data_type}: {source.path.name}")
                
                try:
                    with open(source.path, 'r') as f:
                        data = json.load(f)
                    
                    # Process different data types
                    if source.data_type == "coordination":
                        spans_processed = self._process_coordination_data(data, aggregated_data)
                    elif source.data_type == "swarm":
                        spans_processed = self._process_swarm_data(data, aggregated_data)
                    elif source.data_type == "validation":
                        spans_processed = self._process_validation_data(data, aggregated_data)
                    elif source.data_type == "ecosystem":
                        spans_processed = self._process_ecosystem_data(data, aggregated_data)
                    else:
                        spans_processed = self._process_generic_data(data, aggregated_data)
                    
                    # Update metadata
                    aggregated_data['metadata']['sources_processed'] += 1
                    aggregated_data['metadata']['total_spans'] += spans_processed
                    
                    if source.data_type not in aggregated_data['metadata']['data_types']:
                        aggregated_data['metadata']['data_types'][source.data_type] = 0
                    aggregated_data['metadata']['data_types'][source.data_type] += spans_processed
                    
                    self.session.total_data_processed += source.size_bytes
                    
                except Exception as e:
                    logger.error(f"Error processing {source.path}: {e}")
                
                progress.advance(task)
        
        # Analyze patterns across all data
        aggregated_data['patterns'] = self._analyze_cross_data_patterns(aggregated_data['spans'])
        aggregated_data['insights'] = self._generate_operational_insights(aggregated_data)
        
        return aggregated_data
    
    def _process_coordination_data(self, data: Dict[str, Any], aggregated: Dict[str, Any]) -> int:
        """Process coordination telemetry data"""
        if not isinstance(data, dict):
            return 0
            
        # Extract metrics
        if 'metrics' in data:
            metrics = data['metrics']
            coord_metrics = {
                'coordination_response_time_ms': metrics.get('response_time_ms', 0),
                'coordination_success_rate': metrics.get('success_rate', 0),
                'coordination_model': metrics.get('model', 'unknown')
            }
            aggregated['metrics'].update(coord_metrics)
        
        # Create synthetic spans for coordination events
        span = {
            'name': 'agent.coordination.execute',
            'trace_id': f"coord_{uuid.uuid4().hex[:16]}",
            'span_id': f"span_{uuid.uuid4().hex[:16]}",
            'timestamp': data.get('timestamp', time.time()),
            'attributes': {
                'coordination.type': 'agent_coordination',
                'source.type': 'coordination',
                **data.get('metrics', {})
            },
            'status': 'OK'
        }
        aggregated['spans'].append(span)
        return 1
    
    def _process_swarm_data(self, data: List[Dict[str, Any]], aggregated: Dict[str, Any]) -> int:
        """Process swarm agent telemetry data"""
        if not isinstance(data, list):
            return 0
        
        spans_added = 0
        for event in data:
            if isinstance(event, dict) and 'event' in event:
                span = {
                    'name': f"swarm.agent.{event['event']}",
                    'trace_id': f"swarm_{uuid.uuid4().hex[:16]}",
                    'span_id': f"span_{uuid.uuid4().hex[:16]}",
                    'timestamp': event.get('timestamp', time.time()),
                    'attributes': {
                        'swarm.event': event['event'],
                        'source.type': 'swarm',
                        **event.get('data', {})
                    },
                    'status': 'OK'
                }
                aggregated['spans'].append(span)
                spans_added += 1
        
        return spans_added
    
    def _process_validation_data(self, data: Dict[str, Any], aggregated: Dict[str, Any]) -> int:
        """Process validation telemetry data"""
        spans_added = 0
        
        if 'spans' in data and isinstance(data['spans'], list):
            for span_data in data['spans']:
                if isinstance(span_data, dict):
                    # Normalize span format
                    span = {
                        'name': span_data.get('name', 'validation.unknown'),
                        'trace_id': span_data.get('trace_id', f"val_{uuid.uuid4().hex[:16]}"),
                        'span_id': span_data.get('span_id', f"span_{uuid.uuid4().hex[:16]}"),
                        'timestamp': span_data.get('start_time', time.time()),
                        'duration_ms': (span_data.get('end_time', 0) - span_data.get('start_time', 0)) * 1000,
                        'attributes': {
                            'source.type': 'validation',
                            **span_data.get('attributes', {})
                        },
                        'status': span_data.get('status', 'OK')
                    }
                    aggregated['spans'].append(span)
                    spans_added += 1
        
        # Add metrics
        if 'metrics' in data:
            metrics = data['metrics']
            aggregated['metrics'].update({
                'validation_avg_duration_ms': metrics.get('test.duration.ms', []),
                'validation_success_rates': metrics.get('test.validations.passed', [])
            })
        
        return spans_added
    
    def _process_ecosystem_data(self, data: Dict[str, Any], aggregated: Dict[str, Any]) -> int:
        """Process ecosystem test data"""
        if 'test_results' in data:
            test_results = data['test_results']
            
            # Create spans for each test component
            spans_added = 0
            for component, result in test_results.items():
                span = {
                    'name': f"ecosystem.test.{component}",
                    'trace_id': f"eco_{uuid.uuid4().hex[:16]}",
                    'span_id': f"span_{uuid.uuid4().hex[:16]}",
                    'timestamp': data.get('timestamp', time.time()),
                    'attributes': {
                        'ecosystem.component': component,
                        'test.result': result,
                        'source.type': 'ecosystem'
                    },
                    'status': 'OK' if result else 'ERROR'
                }
                aggregated['spans'].append(span)
                spans_added += 1
            
            # Add ecosystem metrics
            if 'summary' in data:
                summary = data['summary']
                aggregated['metrics'].update({
                    'ecosystem_total_tests': summary.get('total_tests', 0),
                    'ecosystem_passed': summary.get('passed', 0),
                    'ecosystem_success_rate': summary.get('success_rate', 0)
                })
            
            return spans_added
        
        return 0
    
    def _process_generic_data(self, data: Any, aggregated: Dict[str, Any]) -> int:
        """Process generic telemetry data"""
        # Try to extract span-like data from any structure
        spans_added = 0
        
        if isinstance(data, dict):
            if 'spans' in data:
                spans_added = self._process_validation_data(data, aggregated)
            elif 'events' in data:
                spans_added = self._process_swarm_data(data['events'], aggregated)
            else:
                # Create a generic span
                span = {
                    'name': 'generic.telemetry.event',
                    'trace_id': f"gen_{uuid.uuid4().hex[:16]}",
                    'span_id': f"span_{uuid.uuid4().hex[:16]}",
                    'timestamp': time.time(),
                    'attributes': {
                        'source.type': 'generic',
                        'data.keys': list(data.keys())[:10]  # Limit to avoid huge attributes
                    },
                    'status': 'OK'
                }
                aggregated['spans'].append(span)
                spans_added = 1
        
        return spans_added
    
    def _analyze_cross_data_patterns(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across all aggregated data"""
        
        patterns = {
            'span_name_frequency': {},
            'temporal_patterns': {},
            'attribute_patterns': {},
            'status_distribution': {},
            'source_distribution': {},
            'performance_patterns': {}
        }
        
        # Analyze span name patterns
        for span in spans:
            name = span.get('name', 'unknown')
            patterns['span_name_frequency'][name] = patterns['span_name_frequency'].get(name, 0) + 1
            
            # Status distribution
            status = span.get('status', 'UNKNOWN')
            patterns['status_distribution'][status] = patterns['status_distribution'].get(status, 0) + 1
            
            # Source distribution
            source = span.get('attributes', {}).get('source.type', 'unknown')
            patterns['source_distribution'][source] = patterns['source_distribution'].get(source, 0) + 1
            
            # Duration patterns
            duration = span.get('duration_ms', 0)
            if duration > 0:
                if 'durations' not in patterns['performance_patterns']:
                    patterns['performance_patterns']['durations'] = []
                patterns['performance_patterns']['durations'].append(duration)
        
        # Calculate performance statistics
        if patterns['performance_patterns'].get('durations'):
            durations = patterns['performance_patterns']['durations']
            patterns['performance_patterns'].update({
                'avg_duration_ms': statistics.mean(durations),
                'max_duration_ms': max(durations),
                'min_duration_ms': min(durations),
                'p95_duration_ms': sorted(durations)[int(len(durations) * 0.95)] if durations else 0
            })
        
        return patterns
    
    def _generate_operational_insights(self, aggregated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate operational insights from aggregated data"""
        
        insights = {
            'system_health': {},
            'performance_insights': {},
            'operational_patterns': {},
            'recommendations': []
        }
        
        patterns = aggregated_data['patterns']
        spans = aggregated_data['spans']
        
        # System health analysis
        total_spans = len(spans)
        successful_spans = patterns['status_distribution'].get('OK', 0)
        error_spans = patterns['status_distribution'].get('ERROR', 0)
        
        insights['system_health'] = {
            'total_operations': total_spans,
            'success_rate': successful_spans / total_spans if total_spans > 0 else 0,
            'error_rate': error_spans / total_spans if total_spans > 0 else 0,
            'health_score': successful_spans / total_spans if total_spans > 0 else 0
        }
        
        # Performance insights
        if patterns['performance_patterns'].get('avg_duration_ms'):
            perf = patterns['performance_patterns']
            insights['performance_insights'] = {
                'average_operation_time': f"{perf['avg_duration_ms']:.2f}ms",
                'performance_variability': perf['max_duration_ms'] - perf['min_duration_ms'],
                'performance_score': min(1.0, 100 / perf['avg_duration_ms']) if perf['avg_duration_ms'] > 0 else 1.0
            }
        
        # Operational patterns
        most_common_operation = max(patterns['span_name_frequency'].items(), 
                                  key=lambda x: x[1]) if patterns['span_name_frequency'] else ('none', 0)
        
        insights['operational_patterns'] = {
            'dominant_operation': most_common_operation[0],
            'operation_frequency': most_common_operation[1],
            'unique_operations': len(patterns['span_name_frequency']),
            'data_source_diversity': len(patterns['source_distribution'])
        }
        
        # Generate recommendations
        recommendations = []
        
        if insights['system_health']['error_rate'] > 0.1:
            recommendations.append("High error rate detected - investigate failing operations")
        
        if insights['performance_insights'].get('performance_score', 1) < 0.7:
            recommendations.append("Performance optimization needed - consider caching or async processing")
        
        if insights['operational_patterns']['unique_operations'] < 5:
            recommendations.append("Limited operational diversity - consider expanding telemetry coverage")
        
        insights['recommendations'] = recommendations
        
        return insights
    
    async def feed_to_language_model(self, aggregated_data: Dict[str, Any], 
                                   model: str = "ollama/qwen3") -> Dict[str, Any]:
        """Feed aggregated OTEL data to language model for learning"""
        
        # Initialize language model
        lm = init_lm(model=model, experimental=True)
        
        # Prepare learning prompt with telemetry data
        learning_prompt = self._create_learning_prompt(aggregated_data)
        
        console.print(Panel(
            f"[bold cyan]🧠 Feeding OTEL Data to Language Model[/bold cyan]\n"
            f"Model: {model}\n"
            f"Total Spans: {len(aggregated_data['spans'])}\n"
            f"Data Sources: {aggregated_data['metadata']['sources_processed']}\n"
            f"Session: {self.session.session_id}",
            title="LM Learning Session"
        ))
        
        try:
            # Query the language model with telemetry patterns
            import dspy
            
            class OTELLearner(dspy.Signature):
                """Learn from OpenTelemetry operational data to understand system patterns"""
                telemetry_data = dspy.InputField(desc="Aggregated OTEL telemetry data with spans, metrics, and patterns")
                operational_insights = dspy.OutputField(desc="Key insights about system operation patterns, performance characteristics, and recommendations")
                learned_patterns = dspy.OutputField(desc="Extracted patterns that can inform future system decisions")
                
            learner = dspy.Predict(OTELLearner)
            
            # Execute learning
            with console.status("🤔 Language model analyzing telemetry data..."):
                result = learner(telemetry_data=learning_prompt)
            
            # Store insights
            self.session.model_insights.append({
                'timestamp': datetime.utcnow().isoformat(),
                'model': model,
                'operational_insights': result.operational_insights,
                'learned_patterns': result.learned_patterns,
                'data_processed': len(aggregated_data['spans'])
            })
            
            return {
                'success': True,
                'model': model,
                'insights': result.operational_insights,
                'patterns': result.learned_patterns,
                'spans_analyzed': len(aggregated_data['spans']),
                'session_id': self.session.session_id
            }
            
        except Exception as e:
            logger.error(f"Error feeding data to language model: {e}")
            return {
                'success': False,
                'error': str(e),
                'model': model,
                'session_id': self.session.session_id
            }
    
    def _create_learning_prompt(self, aggregated_data: Dict[str, Any]) -> str:
        """Create comprehensive learning prompt from aggregated data"""
        
        patterns = aggregated_data['patterns']
        insights = aggregated_data['insights']
        metadata = aggregated_data['metadata']
        
        # Sample representative spans
        spans_sample = aggregated_data['spans'][:50]  # Limit for token efficiency
        
        prompt = f"""
# OpenTelemetry Operational Learning Data

## System Overview
- **Session**: {metadata['session_id']}
- **Total Operations**: {metadata['total_spans']} spans from {metadata['sources_processed']} sources
- **Data Sources**: {', '.join(metadata['data_types'].keys())}
- **Collection Time**: {metadata['aggregation_timestamp']}

## Operational Patterns
### Most Frequent Operations:
{self._format_frequency_data(patterns['span_name_frequency'])}

### System Health Metrics:
- **Success Rate**: {insights['system_health']['success_rate']:.1%}
- **Error Rate**: {insights['system_health']['error_rate']:.1%}
- **Health Score**: {insights['system_health']['health_score']:.2f}

### Performance Characteristics:
{self._format_performance_data(patterns.get('performance_patterns', {}))}

### Data Source Distribution:
{self._format_frequency_data(patterns['source_distribution'])}

## Representative Operations Sample:
{self._format_spans_sample(spans_sample)}

## Current System Insights:
{insights.get('recommendations', [])}

## Learning Objectives:
Please analyze this operational telemetry data to:
1. Identify key system behavior patterns
2. Understand performance characteristics
3. Recommend operational improvements
4. Extract patterns that could inform future system decisions
5. Highlight any anomalies or areas of concern

Focus on practical insights that could improve system reliability, performance, and observability.
"""
        
        return prompt
    
    def _format_frequency_data(self, freq_data: Dict[str, int]) -> str:
        """Format frequency data for learning prompt"""
        if not freq_data:
            return "No data available"
        
        sorted_items = sorted(freq_data.items(), key=lambda x: x[1], reverse=True)[:10]
        return "\n".join([f"- {name}: {count} occurrences" for name, count in sorted_items])
    
    def _format_performance_data(self, perf_data: Dict[str, Any]) -> str:
        """Format performance data for learning prompt"""
        if not perf_data:
            return "No performance data available"
        
        lines = []
        if 'avg_duration_ms' in perf_data:
            lines.append(f"- Average Duration: {perf_data['avg_duration_ms']:.2f}ms")
        if 'max_duration_ms' in perf_data:
            lines.append(f"- Maximum Duration: {perf_data['max_duration_ms']:.2f}ms")
        if 'p95_duration_ms' in perf_data:
            lines.append(f"- P95 Duration: {perf_data['p95_duration_ms']:.2f}ms")
        
        return "\n".join(lines) if lines else "No performance metrics"
    
    def _format_spans_sample(self, spans: List[Dict[str, Any]]) -> str:
        """Format spans sample for learning prompt"""
        if not spans:
            return "No spans available"
        
        formatted_spans = []
        for i, span in enumerate(spans[:10]):  # Show first 10 spans
            formatted_spans.append(
                f"{i+1}. {span.get('name', 'unknown')} "
                f"[{span.get('status', 'unknown')}] "
                f"({span.get('attributes', {}).get('source.type', 'unknown')} source)"
            )
        
        return "\n".join(formatted_spans)
    
    def generate_learning_report(self, learning_result: Dict[str, Any]) -> None:
        """Generate comprehensive learning report"""
        
        console.print(Panel(
            f"[bold green]🎓 OTEL Learning Complete[/bold green]\n"
            f"Session: {learning_result['session_id']}\n"
            f"Model: {learning_result['model']}\n"
            f"Spans Analyzed: {learning_result['spans_analyzed']}\n"
            f"Success: {'✅' if learning_result['success'] else '❌'}",
            title="Learning Session Results"
        ))
        
        if learning_result['success']:
            # Display insights
            console.print("\n📊 **Model Insights:**")
            console.print(learning_result['insights'])
            
            console.print("\n🔍 **Learned Patterns:**")
            console.print(learning_result['patterns'])
            
            # Display session summary
            summary_table = Table(title="📋 Learning Session Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")
            
            summary_table.add_row("Data Sources", str(len(self.session.data_sources)))
            summary_table.add_row("Total Spans", str(len(self.session.aggregated_spans)))
            summary_table.add_row("Data Processed", f"{self.session.total_data_processed:,} bytes")
            summary_table.add_row("Learning Model", learning_result['model'])
            summary_table.add_row("Session Duration", f"{time.time() - time.time():.2f}s")
            
            console.print(summary_table)
        else:
            console.print(f"\n❌ **Learning Error**: {learning_result.get('error', 'Unknown error')}")


@app.command("learn")
def run_otel_learning(
    base_path: Optional[Path] = typer.Option(None, "--path", "-p", help="Base path to search for OTEL data"),
    model: str = typer.Option("ollama/qwen3", "--model", "-m", help="Language model to use for learning"),
    save_results: bool = typer.Option(True, "--save", help="Save learning results to file")
):
    """Run complete OTEL learning process - gather data and feed to language model"""
    
    with json_command("otel-learning") as formatter:
        try:
            console.print("🧠 OTEL Learning Engine Starting...")
            console.print("=" * 50)
            
            # Initialize learning engine
            engine = OTELLearningEngine(base_path)
            
            # Discover data sources
            console.print("\n🔍 **Phase 1: Discovery**")
            sources = asyncio.run(engine.discover_otel_sources())
            
            console.print(f"✅ Found {len(sources)} OTEL data sources")
            formatter.add_data("sources_discovered", len(sources))
            
            # Aggregate telemetry data
            console.print("\n📊 **Phase 2: Aggregation**")
            aggregated_data = asyncio.run(engine.aggregate_telemetry_data())
            
            console.print(f"✅ Aggregated {aggregated_data['metadata']['total_spans']} spans")
            formatter.add_data("spans_aggregated", aggregated_data['metadata']['total_spans'])
            
            # Feed to language model
            console.print("\n🧠 **Phase 3: Learning**")
            learning_result = asyncio.run(engine.feed_to_language_model(aggregated_data, model))
            
            formatter.add_data("learning_result", learning_result)
            
            # Generate report
            console.print("\n📋 **Phase 4: Reporting**")
            engine.generate_learning_report(learning_result)
            
            # Save results if requested
            if save_results and learning_result['success']:
                results_file = Path(f"otel_learning_{engine.session.session_id}.json")
                with open(results_file, 'w') as f:
                    json.dump({
                        'session': engine.session.__dict__,
                        'aggregated_data': aggregated_data,
                        'learning_result': learning_result
                    }, f, indent=2, default=str)
                console.print(f"✅ Results saved to {results_file}")
            
            formatter.add_data("learning_successful", learning_result['success'])
            
            if learning_result['success']:
                console.print("\n🎉 **OTEL Learning Complete!**")
                console.print("The language model has successfully learned from operational telemetry patterns.")
            else:
                console.print("\n⚠️ **Learning Incomplete**")
                raise typer.Exit(1)
                
        except Exception as e:
            formatter.add_error(f"OTEL learning failed: {e}")
            console.print(f"❌ OTEL learning failed: {e}")
            raise typer.Exit(1)


@app.command("sources")
def show_otel_sources(
    base_path: Optional[Path] = typer.Option(None, "--path", "-p", help="Base path to search for OTEL data")
):
    """Show all discoverable OTEL data sources"""
    
    engine = OTELLearningEngine(base_path)
    sources = asyncio.run(engine.discover_otel_sources())
    
    console.print("🔍 OTEL Data Sources Discovery")
    console.print("=" * 40)
    
    if not sources:
        console.print("No OTEL data sources found")
        return
    
    # Group by data type
    by_type = {}
    for source in sources:
        if source.data_type not in by_type:
            by_type[source.data_type] = []
        by_type[source.data_type].append(source)
    
    # Display sources by type
    for data_type, type_sources in by_type.items():
        console.print(f"\n📊 **{data_type.title()} Sources** ({len(type_sources)} files)")
        
        table = Table()
        table.add_column("File", style="cyan")
        table.add_column("Size", style="yellow")
        table.add_column("Spans", style="green")
        table.add_column("Modified", style="dim")
        
        for source in type_sources:
            table.add_row(
                source.path.name,
                f"{source.size_bytes:,} bytes",
                str(source.span_count),
                source.last_modified.strftime("%Y-%m-%d %H:%M") if source.last_modified else "Unknown"
            )
        
        console.print(table)
    
    # Summary
    total_sources = len(sources)
    total_spans = sum(source.span_count for source in sources)
    total_size = sum(source.size_bytes for source in sources)
    
    console.print(Panel(
        f"📈 **Discovery Summary**\n"
        f"Total Sources: {total_sources}\n"
        f"Total Spans: {total_spans:,}\n"
        f"Total Size: {total_size:,} bytes\n"
        f"Data Types: {len(by_type)}",
        title="OTEL Sources Summary"
    ))


if __name__ == "__main__":
    app()