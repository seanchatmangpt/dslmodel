"""
Analysis Components for Evolution Framework
Autonomous analysis of code quality, performance, security, and architecture
"""

import ast
import re
import subprocess
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import asyncio
import hashlib

from dslmodel import DSLModel
from pydantic import Field

from .core import EvolutionStrategy

class AnalysisResult(DSLModel):
    """Base class for analysis results"""
    analyzer_name: str = Field(..., description="Name of analyzer")
    target_path: Path = Field(..., description="Path analyzed")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    score: float = Field(..., ge=0.0, le=1.0, description="Overall score")
    findings: List[str] = Field(default_factory=list, description="Key findings")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Detailed metrics")

class CodeAnalyzer:
    """Analyzes code structure, complexity, and patterns"""
    
    def __init__(self):
        self.name = "CodeAnalyzer"
        
    async def analyze(self, target_path: Path) -> AnalysisResult:
        """Perform comprehensive code analysis"""
        
        # Collect Python files
        python_files = list(target_path.rglob("*.py"))
        
        if not python_files:
            return AnalysisResult(
                analyzer_name=self.name,
                target_path=target_path,
                score=0.5,
                findings=["No Python files found"],
                recommendations=["Add Python implementation files"]
            )
        
        # Analyze code metrics
        total_lines = 0
        total_complexity = 0
        function_count = 0
        class_count = 0
        issues = []
        
        for py_file in python_files:
            try:
                file_analysis = await self._analyze_file(py_file)
                total_lines += file_analysis['lines']
                total_complexity += file_analysis['complexity']
                function_count += file_analysis['functions']
                class_count += file_analysis['classes']
                issues.extend(file_analysis['issues'])
            except Exception as e:
                issues.append(f"Failed to analyze {py_file}: {str(e)}")
        
        # Calculate metrics
        avg_complexity = total_complexity / max(function_count, 1)
        lines_per_file = total_lines / len(python_files)
        
        # Calculate score
        complexity_score = max(0, 1.0 - (avg_complexity - 5) / 15)  # Ideal complexity ~5
        size_score = max(0, 1.0 - (lines_per_file - 100) / 400)  # Ideal ~100 lines per file
        issue_score = max(0, 1.0 - len(issues) / (len(python_files) * 5))  # Max 5 issues per file
        
        overall_score = (complexity_score + size_score + issue_score) / 3
        
        # Generate findings and recommendations
        findings = [
            f"Analyzed {len(python_files)} Python files",
            f"Total lines: {total_lines}",
            f"Average complexity: {avg_complexity:.1f}",
            f"Functions: {function_count}, Classes: {class_count}",
            f"Issues found: {len(issues)}"
        ]
        
        recommendations = []
        if avg_complexity > 10:
            recommendations.append("Reduce function complexity through refactoring")
        if lines_per_file > 300:
            recommendations.append("Consider breaking large files into smaller modules")
        if len(issues) > len(python_files) * 2:
            recommendations.append("Address code quality issues identified")
        
        return AnalysisResult(
            analyzer_name=self.name,
            target_path=target_path,
            score=overall_score,
            findings=findings,
            recommendations=recommendations,
            metrics={
                "total_lines": total_lines,
                "avg_complexity": avg_complexity,
                "lines_per_file": lines_per_file,
                "function_count": function_count,
                "class_count": class_count,
                "issues": issues[:10]  # Top 10 issues
            }
        )
    
    async def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual Python file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            lines = len(content.splitlines())
            complexity = self._calculate_complexity(tree)
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            issues = self._detect_issues(content, tree)
            
            return {
                'lines': lines,
                'complexity': complexity,
                'functions': functions,
                'classes': classes,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'lines': 0,
                'complexity': 0,
                'functions': 0,
                'classes': 0,
                'issues': [f"Parse error: {str(e)}"]
            }
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _detect_issues(self, content: str, tree: ast.AST) -> List[str]:
        """Detect code quality issues"""
        issues = []
        
        # Check for long lines
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append(f"Line {i+1}: Line too long ({len(line)} > 120)")
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append(f"Missing docstring: {node.name}")
        
        # Check for TODO/FIXME comments
        todo_pattern = re.compile(r'(TODO|FIXME|XXX)', re.IGNORECASE)
        for i, line in enumerate(lines):
            if todo_pattern.search(line):
                issues.append(f"Line {i+1}: TODO/FIXME comment found")
        
        return issues
    
    async def evaluate_fitness(self, target_path: Path) -> float:
        """Evaluate code quality fitness score"""
        result = await self.analyze(target_path)
        return result.score

class PerformanceAnalyzer:
    """Analyzes system performance characteristics"""
    
    def __init__(self):
        self.name = "PerformanceAnalyzer"
        
    async def analyze(self, target_path: Path) -> AnalysisResult:
        """Analyze performance characteristics"""
        
        # Look for performance patterns
        performance_issues = []
        optimization_opportunities = []
        
        python_files = list(target_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                
                # Check for performance anti-patterns
                if re.search(r'for.*in.*range\(len\(', content):
                    performance_issues.append(f"{py_file.name}: Use enumerate() instead of range(len())")
                
                if re.search(r'\.append\(.*\)\s*for.*in', content):
                    optimization_opportunities.append(f"{py_file.name}: Consider list comprehension")
                
                if re.search(r'import\s+pandas', content):
                    optimization_opportunities.append(f"{py_file.name}: Review pandas usage for performance")
                
                # Check for inefficient patterns
                if content.count('+=') > 10:
                    optimization_opportunities.append(f"{py_file.name}: Many string concatenations - consider join()")
                
            except Exception:
                continue
        
        # Calculate performance score
        issue_count = len(performance_issues)
        opportunity_count = len(optimization_opportunities)
        total_files = len(python_files) if python_files else 1
        
        issue_ratio = issue_count / total_files
        performance_score = max(0.0, 1.0 - issue_ratio * 0.5)
        
        findings = [
            f"Analyzed {total_files} files for performance",
            f"Performance issues: {issue_count}",
            f"Optimization opportunities: {opportunity_count}"
        ]
        
        recommendations = []
        if issue_count > 0:
            recommendations.append("Address identified performance anti-patterns")
        if opportunity_count > 0:
            recommendations.append("Consider optimization opportunities")
        if opportunity_count > total_files:
            recommendations.append("Implement comprehensive performance profiling")
        
        return AnalysisResult(
            analyzer_name=self.name,
            target_path=target_path,
            score=performance_score,
            findings=findings,
            recommendations=recommendations,
            metrics={
                "performance_issues": performance_issues[:5],
                "optimization_opportunities": optimization_opportunities[:5],
                "issue_ratio": issue_ratio
            }
        )
    
    async def evaluate_fitness(self, target_path: Path) -> float:
        """Evaluate performance fitness score"""
        result = await self.analyze(target_path)
        return result.score

class SecurityAnalyzer:
    """Analyzes security vulnerabilities and patterns"""
    
    def __init__(self):
        self.name = "SecurityAnalyzer"
        
    async def analyze(self, target_path: Path) -> AnalysisResult:
        """Analyze security vulnerabilities"""
        
        security_issues = []
        python_files = list(target_path.rglob("*.py"))
        
        # Security patterns to check
        security_patterns = {
            r'eval\s*\(': "Code injection risk: eval() usage",
            r'exec\s*\(': "Code injection risk: exec() usage", 
            r'os\.system\s*\(': "Command injection risk: os.system() usage",
            r'subprocess.*shell\s*=\s*True': "Command injection risk: shell=True",
            r'password\s*=\s*[\'"][^\'"]+[\'"]': "Hardcoded password",
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]': "Hardcoded API key",
            r'hashlib\.md5\s*\(': "Weak crypto: MD5 usage",
            r'hashlib\.sha1\s*\(': "Weak crypto: SHA1 usage",
            r'random\.random\s*\(': "Weak randomness for crypto",
            r'ssl.*verify\s*=\s*False': "SSL verification disabled"
        }
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                
                for pattern, description in security_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        security_issues.append(f"{py_file.name}: {description}")
                        
            except Exception:
                continue
        
        # Calculate security score
        total_files = len(python_files) if python_files else 1
        issue_ratio = len(security_issues) / total_files
        security_score = max(0.0, 1.0 - issue_ratio * 0.3)
        
        findings = [
            f"Scanned {total_files} files for security issues",
            f"Security vulnerabilities found: {len(security_issues)}"
        ]
        
        recommendations = []
        if len(security_issues) > 0:
            recommendations.append("Address identified security vulnerabilities")
            recommendations.append("Implement input validation and sanitization")
            recommendations.append("Use secure cryptographic functions")
        
        if len(security_issues) > total_files:
            recommendations.append("Conduct comprehensive security audit")
        
        return AnalysisResult(
            analyzer_name=self.name,
            target_path=target_path,
            score=security_score,
            findings=findings,
            recommendations=recommendations,
            metrics={
                "security_issues": security_issues[:10],
                "issue_ratio": issue_ratio,
                "critical_count": len([i for i in security_issues if "injection" in i.lower()])
            }
        )
    
    async def evaluate_fitness(self, target_path: Path) -> float:
        """Evaluate security fitness score"""
        result = await self.analyze(target_path)
        return result.score

class QualityAnalyzer:
    """Analyzes overall code quality metrics"""
    
    def __init__(self):
        self.name = "QualityAnalyzer"
        
    async def analyze(self, target_path: Path) -> AnalysisResult:
        """Analyze code quality metrics"""
        
        python_files = list(target_path.rglob("*.py"))
        
        if not python_files:
            return AnalysisResult(
                analyzer_name=self.name,
                target_path=target_path,
                score=0.5,
                findings=["No Python files to analyze"]
            )
        
        # Quality metrics
        total_lines = 0
        documented_functions = 0
        total_functions = 0
        test_files = 0
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                total_lines += len(content.splitlines())
                
                # Count test files
                if 'test' in py_file.name.lower():
                    test_files += 1
                
                # Count functions and documentation
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        if ast.get_docstring(node):
                            documented_functions += 1
                            
            except Exception:
                continue
        
        # Calculate quality metrics
        documentation_ratio = documented_functions / max(total_functions, 1)
        test_ratio = test_files / len(python_files)
        
        # Quality score calculation
        doc_score = documentation_ratio
        test_score = min(test_ratio * 2, 1.0)  # Boost test score
        
        quality_score = (doc_score + test_score) / 2
        
        findings = [
            f"Analyzed {len(python_files)} Python files",
            f"Total lines of code: {total_lines}",
            f"Functions documented: {documented_functions}/{total_functions} ({documentation_ratio:.1%})",
            f"Test files: {test_files}/{len(python_files)} ({test_ratio:.1%})"
        ]
        
        recommendations = []
        if documentation_ratio < 0.8:
            recommendations.append("Improve documentation coverage")
        if test_ratio < 0.2:
            recommendations.append("Add more test files")
        if total_lines / len(python_files) > 200:
            recommendations.append("Consider breaking large files into smaller modules")
        
        return AnalysisResult(
            analyzer_name=self.name,
            target_path=target_path,
            score=quality_score,
            findings=findings,
            recommendations=recommendations,
            metrics={
                "documentation_ratio": documentation_ratio,
                "test_ratio": test_ratio,
                "avg_file_size": total_lines / len(python_files),
                "total_functions": total_functions
            }
        )
    
    async def evaluate_fitness(self, target_path: Path) -> float:
        """Evaluate quality fitness score"""
        result = await self.analyze(target_path)
        return result.score

class ArchitectureAnalyzer:
    """Analyzes system architecture and design patterns"""
    
    def __init__(self):
        self.name = "ArchitectureAnalyzer"
        
    async def analyze(self, target_path: Path) -> AnalysisResult:
        """Analyze architectural characteristics"""
        
        python_files = list(target_path.rglob("*.py"))
        
        # Architecture metrics
        modules = set()
        imports = []
        class_count = 0
        inheritance_depth = 0
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                # Track modules
                modules.add(py_file.parent.name)
                
                # Analyze imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
                    elif isinstance(node, ast.ClassDef):
                        class_count += 1
                        # Calculate inheritance depth (simplified)
                        if node.bases:
                            inheritance_depth += len(node.bases)
                            
            except Exception:
                continue
        
        # Calculate architecture metrics
        unique_imports = len(set(imports))
        external_deps = len([imp for imp in set(imports) if not imp.startswith('.')])
        internal_deps = len([imp for imp in set(imports) if imp.startswith('.')])
        
        avg_inheritance = inheritance_depth / max(class_count, 1)
        
        # Architecture score
        modularity_score = min(len(modules) / 10, 1.0)  # Good modularity
        coupling_score = max(0, 1.0 - external_deps / 50)  # Lower coupling is better
        cohesion_score = min(internal_deps / max(external_deps, 1), 1.0)
        
        architecture_score = (modularity_score + coupling_score + cohesion_score) / 3
        
        findings = [
            f"Analyzed {len(python_files)} files across {len(modules)} modules",
            f"Total imports: {unique_imports} (external: {external_deps}, internal: {internal_deps})",
            f"Classes: {class_count}, Average inheritance depth: {avg_inheritance:.1f}"
        ]
        
        recommendations = []
        if external_deps > 30:
            recommendations.append("Consider reducing external dependencies")
        if len(modules) < 3 and len(python_files) > 10:
            recommendations.append("Improve modular organization")
        if avg_inheritance > 3:
            recommendations.append("Review inheritance hierarchies for complexity")
        
        return AnalysisResult(
            analyzer_name=self.name,
            target_path=target_path,
            score=architecture_score,
            findings=findings,
            recommendations=recommendations,
            metrics={
                "modules": len(modules),
                "unique_imports": unique_imports,
                "external_deps": external_deps,
                "internal_deps": internal_deps,
                "class_count": class_count,
                "avg_inheritance": avg_inheritance
            }
        )
    
    async def evaluate_fitness(self, target_path: Path) -> float:
        """Evaluate architecture fitness score"""
        result = await self.analyze(target_path)
        return result.score