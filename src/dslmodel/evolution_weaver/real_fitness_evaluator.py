#!/usr/bin/env python3
"""
Real Fitness Evaluator - Replace simulation with actual metrics
80/20 approach: Focus on critical metrics that drive evolution decisions
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass

from opentelemetry import trace


@dataclass
class FitnessMetrics:
    """Real fitness evaluation results"""
    test_success_rate: float  # 0.0 - 1.0
    performance_score: float  # Relative performance vs baseline
    code_quality_score: float  # Static analysis metrics
    error_count: int
    test_execution_time: float  # seconds
    overall_fitness: float  # Combined weighted score
    
    def to_dict(self) -> Dict:
        return {
            'test_success_rate': self.test_success_rate,
            'performance_score': self.performance_score,
            'code_quality_score': self.code_quality_score,
            'error_count': self.error_count,
            'test_execution_time': self.test_execution_time,
            'overall_fitness': self.overall_fitness
        }


class RealFitnessEvaluator:
    """Real fitness evaluation using actual test execution and metrics"""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        
        # Fitness weights for different metrics (80/20 principle)
        self.weights = {
            'test_success': 0.5,    # 50% - Most critical for reliability
            'performance': 0.3,     # 30% - Key for evolution goals
            'code_quality': 0.15,   # 15% - Important for maintainability
            'error_reduction': 0.05  # 5% - Error count penalty
        }
    
    async def evaluate_experiment_fitness(
        self, 
        worktree_path: Path, 
        experiment_id: str,
        strategy: str,
        baseline_metrics: Optional[Dict] = None
    ) -> FitnessMetrics:
        """
        Evaluate real fitness of an experiment using actual metrics
        
        Args:
            worktree_path: Path to the experiment worktree
            experiment_id: Unique experiment identifier
            strategy: Evolution strategy being tested
            baseline_metrics: Baseline metrics for comparison
            
        Returns:
            FitnessMetrics: Real fitness evaluation results
        """
        
        with self.tracer.start_as_current_span("fitness.real_evaluation") as span:
            span.set_attribute("fitness.experiment_id", experiment_id)
            span.set_attribute("fitness.strategy", strategy)
            span.set_attribute("fitness.worktree_path", str(worktree_path))
            
            evaluation_start = time.time()
            
            try:
                # 1. Run actual tests (50% weight)
                test_metrics = await self._run_tests(worktree_path)
                span.set_attribute("fitness.tests_total", test_metrics['total'])
                span.set_attribute("fitness.tests_passed", test_metrics['passed'])
                
                # 2. Measure performance (30% weight)
                performance_metrics = await self._measure_performance(worktree_path, strategy)
                span.set_attribute("fitness.performance_score", performance_metrics['score'])
                
                # 3. Analyze code quality (15% weight)
                quality_metrics = await self._analyze_code_quality(worktree_path)
                span.set_attribute("fitness.quality_score", quality_metrics['score'])
                
                # 4. Calculate overall fitness
                fitness = self._calculate_weighted_fitness(
                    test_metrics, performance_metrics, quality_metrics
                )
                
                evaluation_time = time.time() - evaluation_start
                span.set_attribute("fitness.evaluation_duration", evaluation_time)
                span.set_attribute("fitness.overall_score", fitness.overall_fitness)
                
                return fitness
                
            except Exception as e:
                span.set_attribute("fitness.error", str(e))
                span.set_attribute("fitness.evaluation_failed", True)
                
                # Return minimal fitness for failed evaluations
                return FitnessMetrics(
                    test_success_rate=0.0,
                    performance_score=0.0,
                    code_quality_score=0.0,
                    error_count=1,
                    test_execution_time=time.time() - evaluation_start,
                    overall_fitness=0.1  # Minimal score to avoid division by zero
                )
    
    async def _run_tests(self, worktree_path: Path) -> Dict:
        """Run actual tests and measure success rate"""
        
        try:
            # Change to worktree directory for test execution
            original_cwd = Path.cwd()
            
            # Look for test files in the worktree
            test_files = list(worktree_path.rglob("test_*.py"))
            if not test_files:
                # Fallback: run import tests on Python files
                python_files = list(worktree_path.rglob("*.py"))
                return await self._run_import_tests(python_files)
            
            # Run pytest on discovered test files
            test_cmd = [
                "python", "-m", "pytest", 
                "--tb=no", "--quiet", 
                "--json-report", "--json-report-file=/tmp/pytest_report.json"
            ] + [str(f) for f in test_files[:5]]  # Limit to 5 tests for speed
            
            result = subprocess.run(
                test_cmd,
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Parse pytest results
            try:
                with open("/tmp/pytest_report.json", "r") as f:
                    report = json.load(f)
                    
                return {
                    'total': report['summary']['total'],
                    'passed': report['summary']['passed'],
                    'failed': report['summary']['failed'],
                    'success_rate': report['summary']['passed'] / max(report['summary']['total'], 1)
                }
            except (FileNotFoundError, KeyError, json.JSONDecodeError):
                # Fallback: parse pytest output
                return self._parse_pytest_output(result.stdout)
                
        except subprocess.TimeoutExpired:
            return {'total': 1, 'passed': 0, 'failed': 1, 'success_rate': 0.0}
        except Exception:
            return {'total': 1, 'passed': 0, 'failed': 1, 'success_rate': 0.0}
    
    async def _run_import_tests(self, python_files: List[Path]) -> Dict:
        """Fallback: test that Python files can be imported without errors"""
        
        total = len(python_files)
        passed = 0
        
        for py_file in python_files[:10]:  # Limit to 10 files for speed
            try:
                # Try to compile the Python file
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                compile(content, str(py_file), 'exec')
                passed += 1
                
            except (SyntaxError, IndentationError, TabError):
                # File has syntax errors
                continue
            except Exception:
                # Other import/compilation issues
                continue
        
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': passed / max(total, 1)
        }
    
    def _parse_pytest_output(self, output: str) -> Dict:
        """Parse pytest output when JSON report is not available"""
        
        try:
            # Look for patterns like "5 passed, 2 failed"
            lines = output.split('\n')
            result_line = [line for line in lines if 'passed' in line or 'failed' in line][-1]
            
            passed = 0
            failed = 0
            
            if 'passed' in result_line:
                passed = int(result_line.split('passed')[0].strip().split()[-1])
            if 'failed' in result_line:
                failed = int(result_line.split('failed')[0].strip().split()[-1])
                
            total = passed + failed
            
            return {
                'total': total,
                'passed': passed,
                'failed': failed,
                'success_rate': passed / max(total, 1)
            }
            
        except (ValueError, IndexError):
            return {'total': 1, 'passed': 0, 'failed': 1, 'success_rate': 0.0}
    
    async def _measure_performance(self, worktree_path: Path, strategy: str) -> Dict:
        """Measure performance impact of changes"""
        
        # Strategy-specific performance measurement
        if strategy == "performance":
            return await self._measure_execution_speed(worktree_path)
        elif strategy == "quality":
            return await self._measure_code_complexity(worktree_path)
        else:
            # Generic performance measurement
            return await self._measure_file_metrics(worktree_path)
    
    async def _measure_execution_speed(self, worktree_path: Path) -> Dict:
        """Measure execution speed of Python files"""
        
        try:
            # Find importable Python modules
            python_files = [f for f in worktree_path.rglob("*.py") 
                          if not f.name.startswith("test_")]
            
            if not python_files:
                return {'score': 0.5, 'metric': 'no_files'}
            
            # Time imports (proxy for execution speed)
            import_times = []
            for py_file in python_files[:5]:  # Limit to 5 for speed
                try:
                    start = time.time()
                    spec = compile(py_file.read_text(), str(py_file), 'exec')
                    import_time = time.time() - start
                    import_times.append(import_time)
                except Exception:
                    import_times.append(1.0)  # Penalty for broken imports
            
            avg_import_time = sum(import_times) / len(import_times)
            
            # Convert to score (faster = higher score)
            # 0.1s = 0.9 score, 1.0s = 0.1 score
            score = max(0.1, 1.0 - min(avg_import_time, 0.9))
            
            return {'score': score, 'metric': 'import_speed', 'avg_time': avg_import_time}
            
        except Exception:
            return {'score': 0.5, 'metric': 'measurement_failed'}
    
    async def _measure_code_complexity(self, worktree_path: Path) -> Dict:
        """Measure code complexity reduction"""
        
        try:
            python_files = list(worktree_path.rglob("*.py"))
            if not python_files:
                return {'score': 0.5, 'metric': 'no_files'}
            
            # Simple complexity metrics
            total_lines = 0
            total_functions = 0
            
            for py_file in python_files:
                try:
                    content = py_file.read_text()
                    lines = content.split('\n')
                    
                    # Count non-empty lines
                    code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
                    total_lines += len(code_lines)
                    
                    # Count function definitions
                    function_lines = [line for line in lines if line.strip().startswith('def ')]
                    total_functions += len(function_lines)
                    
                except Exception:
                    continue
            
            # Calculate complexity score (lower complexity = higher score)
            if total_functions == 0:
                complexity = total_lines  # No functions = all complexity
            else:
                complexity = total_lines / total_functions  # Lines per function
            
            # Convert to score (lower complexity = higher score)
            score = max(0.1, 1.0 - min(complexity / 50.0, 0.9))  # 50 lines/func = 0.1 score
            
            return {'score': score, 'metric': 'complexity', 'lines_per_function': complexity}
            
        except Exception:
            return {'score': 0.5, 'metric': 'measurement_failed'}
    
    async def _measure_file_metrics(self, worktree_path: Path) -> Dict:
        """Generic file-based performance metrics"""
        
        try:
            python_files = list(worktree_path.rglob("*.py"))
            if not python_files:
                return {'score': 0.5, 'metric': 'no_files'}
            
            # File size metric (smaller improvements often better)
            total_size = sum(f.stat().st_size for f in python_files)
            avg_file_size = total_size / len(python_files)
            
            # Convert to score (moderate size = higher score)
            # 1KB = 0.9, 10KB = 0.5, 100KB = 0.1
            size_score = max(0.1, 1.0 - min(avg_file_size / 10000, 0.9))
            
            return {'score': size_score, 'metric': 'file_size', 'avg_size': avg_file_size}
            
        except Exception:
            return {'score': 0.5, 'metric': 'measurement_failed'}
    
    async def _analyze_code_quality(self, worktree_path: Path) -> Dict:
        """Analyze code quality metrics"""
        
        try:
            # Simple quality metrics
            python_files = list(worktree_path.rglob("*.py"))
            if not python_files:
                return {'score': 0.5, 'metric': 'no_files'}
            
            quality_score = 0.5  # Start with neutral score
            
            # Check for docstrings
            files_with_docstrings = 0
            syntax_errors = 0
            
            for py_file in python_files:
                try:
                    content = py_file.read_text()
                    
                    # Check for syntax errors
                    compile(content, str(py_file), 'exec')
                    
                    # Check for docstrings
                    if '"""' in content or "'''" in content:
                        files_with_docstrings += 1
                        
                except (SyntaxError, IndentationError):
                    syntax_errors += 1
                except Exception:
                    continue
            
            # Calculate quality score
            if len(python_files) > 0:
                docstring_ratio = files_with_docstrings / len(python_files)
                error_ratio = syntax_errors / len(python_files)
                
                quality_score = (docstring_ratio * 0.6) + (1.0 - error_ratio) * 0.4
            
            return {
                'score': max(0.1, min(quality_score, 1.0)),
                'metric': 'combined_quality',
                'docstring_ratio': files_with_docstrings / max(len(python_files), 1),
                'syntax_errors': syntax_errors
            }
            
        except Exception:
            return {'score': 0.5, 'metric': 'measurement_failed'}
    
    def _calculate_weighted_fitness(
        self, 
        test_metrics: Dict, 
        performance_metrics: Dict, 
        quality_metrics: Dict
    ) -> FitnessMetrics:
        """Calculate overall fitness using weighted scores"""
        
        # Extract scores
        test_score = test_metrics.get('success_rate', 0.0)
        perf_score = performance_metrics.get('score', 0.5)
        quality_score = quality_metrics.get('score', 0.5)
        error_count = test_metrics.get('failed', 0)
        
        # Calculate weighted fitness
        fitness = (
            (test_score * self.weights['test_success']) +
            (perf_score * self.weights['performance']) +
            (quality_score * self.weights['code_quality']) -
            (min(error_count * 0.1, 0.5) * self.weights['error_reduction'])  # Error penalty
        )
        
        # Ensure fitness is in valid range
        fitness = max(0.1, min(fitness, 1.0))
        
        return FitnessMetrics(
            test_success_rate=test_score,
            performance_score=perf_score,
            code_quality_score=quality_score,
            error_count=error_count,
            test_execution_time=test_metrics.get('execution_time', 0.0),
            overall_fitness=fitness
        )


# Quick test when run directly
async def main():
    """Test the real fitness evaluator"""
    evaluator = RealFitnessEvaluator()
    
    # Test on current directory
    metrics = await evaluator.evaluate_experiment_fitness(
        worktree_path=Path.cwd(),
        experiment_id="test-001",
        strategy="performance"
    )
    
    print(f"🎯 Real Fitness Evaluation Results:")
    print(f"   Overall Fitness: {metrics.overall_fitness:.3f}")
    print(f"   Test Success Rate: {metrics.test_success_rate:.3f}")
    print(f"   Performance Score: {metrics.performance_score:.3f}")
    print(f"   Quality Score: {metrics.code_quality_score:.3f}")
    print(f"   Error Count: {metrics.error_count}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())