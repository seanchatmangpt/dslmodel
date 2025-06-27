#!/usr/bin/env python3
"""
Multi-Layer Weaver Validation System
====================================

Implements multiple validation layers for weaver-generated code with feedback loops:

Layer 1: Syntax & Structure Validation
Layer 2: Semantic & Behavioral Validation  
Layer 3: Contextual & Quality Validation
Layer 4: Integration & Performance Validation

Each layer provides feedback to improve subsequent generations.
"""

import ast
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class ValidationLayer(Enum):
    """Validation layer types"""
    SYNTAX = "syntax"
    SEMANTIC = "semantic" 
    CONTEXTUAL = "contextual"
    INTEGRATION = "integration"


class ValidationResult(Enum):
    """Validation result types"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    layer: ValidationLayer
    severity: str  # "error", "warning", "info"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class LayerValidationResult:
    """Result from a single validation layer"""
    layer: ValidationLayer
    result: ValidationResult
    score: float  # 0.0 to 1.0
    duration_ms: float
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ValidationFeedback:
    """Feedback for improving weaver generation"""
    overall_score: float
    layer_scores: Dict[ValidationLayer, float]
    common_issues: List[str]
    improvement_suggestions: List[str]
    parameter_adjustments: Dict[str, Any]
    model_recommendations: List[str]


@dataclass
class WeaverGenerationContext:
    """Context for weaver generation"""
    feature_name: str
    semantic_model: str
    generation_parameters: Dict[str, Any]
    previous_attempts: int = 0
    feedback_history: List[ValidationFeedback] = field(default_factory=list)


class Layer1SyntaxValidator:
    """Layer 1: Syntax and structure validation"""
    
    def __init__(self):
        self.name = "Syntax Validator"
    
    async def validate(self, file_path: Path, context: WeaverGenerationContext) -> LayerValidationResult:
        """Validate syntax and basic structure"""
        start_time = time.time()
        issues = []
        metrics = {}
        
        try:
            if file_path.suffix == ".py":
                # Python syntax validation
                content = file_path.read_text()
                
                # 1. AST parsing
                try:
                    tree = ast.parse(content)
                    metrics["ast_nodes"] = len(list(ast.walk(tree)))
                except SyntaxError as e:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.SYNTAX,
                        severity="error",
                        message=f"Syntax error: {e.msg}",
                        file_path=str(file_path),
                        line_number=e.lineno,
                        suggestion="Fix syntax error before proceeding",
                        auto_fixable=False
                    ))
                
                # 2. Import validation
                import_issues = self._validate_imports(content, file_path)
                issues.extend(import_issues)
                
                # 3. Basic structure validation
                structure_issues = self._validate_structure(content, context)
                issues.extend(structure_issues)
                
                # 4. Code formatting
                format_issues = self._validate_formatting(content, file_path)
                issues.extend(format_issues)
                
            elif file_path.suffix == ".json":
                # JSON validation
                try:
                    content = file_path.read_text()
                    json.loads(content)
                except json.JSONDecodeError as e:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.SYNTAX,
                        severity="error",
                        message=f"Invalid JSON: {e.msg}",
                        file_path=str(file_path),
                        line_number=e.lineno,
                        auto_fixable=True
                    ))
            
        except Exception as e:
            logger.error(f"Layer 1 validation error: {e}")
            issues.append(ValidationIssue(
                layer=ValidationLayer.SYNTAX,
                severity="error",
                message=f"Validation failed: {str(e)}",
                auto_fixable=False
            ))
        
        # Calculate score
        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])
        
        if error_count > 0:
            score = 0.0
            result = ValidationResult.FAIL
        elif warning_count > 3:
            score = 0.6
            result = ValidationResult.WARNING
        else:
            score = max(0.8, 1.0 - (warning_count * 0.1))
            result = ValidationResult.PASS
        
        duration_ms = (time.time() - start_time) * 1000
        
        return LayerValidationResult(
            layer=ValidationLayer.SYNTAX,
            result=result,
            score=score,
            duration_ms=duration_ms,
            issues=issues,
            metrics=metrics
        )
    
    def _validate_imports(self, content: str, file_path: Path) -> List[ValidationIssue]:
        """Validate import statements"""
        issues = []
        
        # Check for unused imports (simplified)
        import_lines = [line for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
        
        for i, line in enumerate(import_lines):
            if 'import' in line:
                # Extract module name
                if 'from' in line:
                    parts = line.split('import')
                    if len(parts) > 1:
                        imported = parts[1].strip().split(',')[0].strip()
                else:
                    imported = line.replace('import', '').strip().split()[0]
                
                # Check if used (very basic check)
                if imported not in content.replace(line, ''):
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.SYNTAX,
                        severity="warning",
                        message=f"Potentially unused import: {imported}",
                        file_path=str(file_path),
                        line_number=i + 1,
                        suggestion=f"Remove unused import: {imported}",
                        auto_fixable=True
                    ))
        
        return issues
    
    def _validate_structure(self, content: str, context: WeaverGenerationContext) -> List[ValidationIssue]:
        """Validate code structure expectations"""
        issues = []
        
        # Check for expected elements based on feature type
        if "model" in context.feature_name.lower():
            if "class" not in content:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.SYNTAX,
                    severity="warning",
                    message="Expected class definition for model feature",
                    suggestion="Add a class definition",
                    auto_fixable=False
                ))
        
        if "api" in context.feature_name.lower():
            if "def " not in content and "async def" not in content:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.SYNTAX,
                    severity="warning", 
                    message="Expected function definitions for API feature",
                    suggestion="Add function definitions",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_formatting(self, content: str, file_path: Path) -> List[ValidationIssue]:
        """Validate code formatting"""
        issues = []
        
        lines = content.split('\n')
        
        # Check line length
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.SYNTAX,
                    severity="warning",
                    message=f"Line too long ({len(line)} chars)",
                    file_path=str(file_path),
                    line_number=i + 1,
                    suggestion="Break long lines",
                    auto_fixable=True
                ))
        
        return issues


class Layer2SemanticValidator:
    """Layer 2: Semantic and behavioral validation"""
    
    def __init__(self):
        self.name = "Semantic Validator"
    
    async def validate(self, file_path: Path, context: WeaverGenerationContext) -> LayerValidationResult:
        """Validate semantic correctness and behavior"""
        start_time = time.time()
        issues = []
        metrics = {}
        suggestions = []
        
        try:
            # 1. Type checking with mypy
            type_issues = await self._run_type_checking(file_path)
            issues.extend(type_issues)
            
            # 2. Test execution
            test_results = await self._run_tests(file_path)
            issues.extend(test_results.get("issues", []))
            metrics.update(test_results.get("metrics", {}))
            
            # 3. Code complexity analysis
            complexity_issues = self._analyze_complexity(file_path)
            issues.extend(complexity_issues)
            
            # 4. Security scanning
            security_issues = await self._security_scan(file_path)
            issues.extend(security_issues)
            
            # Generate suggestions based on issues
            suggestions = self._generate_semantic_suggestions(issues, context)
            
        except Exception as e:
            logger.error(f"Layer 2 validation error: {e}")
            issues.append(ValidationIssue(
                layer=ValidationLayer.SEMANTIC,
                severity="error",
                message=f"Semantic validation failed: {str(e)}",
                auto_fixable=False
            ))
        
        # Calculate score
        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])
        
        test_pass_rate = metrics.get("test_pass_rate", 0.0)
        
        if error_count > 0 or test_pass_rate < 0.5:
            score = min(0.4, test_pass_rate)
            result = ValidationResult.FAIL
        elif warning_count > 5 or test_pass_rate < 0.8:
            score = 0.7 * test_pass_rate
            result = ValidationResult.WARNING
        else:
            score = min(0.95, test_pass_rate * 1.1)
            result = ValidationResult.PASS
        
        duration_ms = (time.time() - start_time) * 1000
        
        return LayerValidationResult(
            layer=ValidationLayer.SEMANTIC,
            result=result,
            score=score,
            duration_ms=duration_ms,
            issues=issues,
            metrics=metrics,
            suggestions=suggestions
        )
    
    async def _run_type_checking(self, file_path: Path) -> List[ValidationIssue]:
        """Run mypy type checking"""
        issues = []
        
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", str(file_path), "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                for line in result.stdout.split('\n'):
                    if line.strip() and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            try:
                                line_num = int(parts[1])
                                message = ':'.join(parts[3:]).strip()
                                issues.append(ValidationIssue(
                                    layer=ValidationLayer.SEMANTIC,
                                    severity="warning",
                                    message=f"Type error: {message}",
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    suggestion="Fix type annotations",
                                    auto_fixable=False
                                ))
                            except ValueError:
                                pass
                                
        except Exception as e:
            logger.warning(f"Type checking failed: {e}")
        
        return issues
    
    async def _run_tests(self, file_path: Path) -> Dict[str, Any]:
        """Run tests for the generated code"""
        results = {"issues": [], "metrics": {}}
        
        try:
            # Look for test files
            test_dir = file_path.parent / "tests"
            if test_dir.exists():
                result = subprocess.run(
                    ["python", "-m", "pytest", str(test_dir), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Parse pytest output
                output_lines = result.stdout.split('\n')
                
                total_tests = 0
                passed_tests = 0
                
                for line in output_lines:
                    if "PASSED" in line:
                        passed_tests += 1
                        total_tests += 1
                    elif "FAILED" in line:
                        total_tests += 1
                        # Extract failure info
                        results["issues"].append(ValidationIssue(
                            layer=ValidationLayer.SEMANTIC,
                            severity="error",
                            message=f"Test failed: {line}",
                            suggestion="Fix failing test",
                            auto_fixable=False
                        ))
                
                if total_tests > 0:
                    results["metrics"]["test_pass_rate"] = passed_tests / total_tests
                    results["metrics"]["total_tests"] = total_tests
                    results["metrics"]["passed_tests"] = passed_tests
                else:
                    results["metrics"]["test_pass_rate"] = 1.0  # No tests = pass
            else:
                # No tests found
                results["issues"].append(ValidationIssue(
                    layer=ValidationLayer.SEMANTIC,
                    severity="warning",
                    message="No tests found",
                    suggestion="Add test coverage",
                    auto_fixable=False
                ))
                results["metrics"]["test_pass_rate"] = 0.5  # Neutral
                
        except Exception as e:
            logger.warning(f"Test execution failed: {e}")
            results["metrics"]["test_pass_rate"] = 0.0
        
        return results
    
    def _analyze_complexity(self, file_path: Path) -> List[ValidationIssue]:
        """Analyze code complexity"""
        issues = []
        
        try:
            if file_path.suffix == ".py":
                content = file_path.read_text()
                tree = ast.parse(content)
                
                # Simple cyclomatic complexity estimate
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_complexity(node)
                        if complexity > 10:
                            issues.append(ValidationIssue(
                                layer=ValidationLayer.SEMANTIC,
                                severity="warning",
                                message=f"High complexity function: {node.name} (complexity: {complexity})",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                suggestion="Consider breaking down complex function",
                                auto_fixable=False
                            ))
                            
        except Exception as e:
            logger.warning(f"Complexity analysis failed: {e}")
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    async def _security_scan(self, file_path: Path) -> List[ValidationIssue]:
        """Basic security scanning"""
        issues = []
        
        try:
            if file_path.suffix == ".py":
                content = file_path.read_text()
                
                # Check for common security issues
                security_patterns = [
                    (r'eval\s*\(', "Use of eval() is dangerous"),
                    (r'exec\s*\(', "Use of exec() is dangerous"),
                    (r'os\.system\s*\(', "Use of os.system() can be unsafe"),
                    (r'subprocess\.call\s*\([^)]*shell=True', "Shell=True in subprocess can be unsafe"),
                    (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
                    (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected")
                ]
                
                for pattern, message in security_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append(ValidationIssue(
                            layer=ValidationLayer.SEMANTIC,
                            severity="warning",
                            message=f"Security: {message}",
                            file_path=str(file_path),
                            line_number=line_num,
                            suggestion="Review security implications",
                            auto_fixable=False
                        ))
                        
        except Exception as e:
            logger.warning(f"Security scan failed: {e}")
        
        return issues
    
    def _generate_semantic_suggestions(self, issues: List[ValidationIssue], context: WeaverGenerationContext) -> List[str]:
        """Generate suggestions based on semantic issues"""
        suggestions = []
        
        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])
        
        if error_count > 5:
            suggestions.append("Consider using a simpler semantic model")
            suggestions.append("Break down into smaller components")
        
        if warning_count > 10:
            suggestions.append("Increase code quality constraints in weaver spec")
            suggestions.append("Add more specific type annotations")
        
        # Security-specific suggestions
        security_issues = [i for i in issues if "Security:" in i.message]
        if security_issues:
            suggestions.append("Add security-focused weaver constraints")
            suggestions.append("Use secure coding patterns in generation")
        
        return suggestions


class Layer3ContextualValidator:
    """Layer 3: Contextual and quality validation"""
    
    def __init__(self):
        self.name = "Contextual Validator"
    
    async def validate(self, file_path: Path, context: WeaverGenerationContext) -> LayerValidationResult:
        """Validate contextual appropriateness and quality"""
        start_time = time.time()
        issues = []
        metrics = {}
        suggestions = []
        
        try:
            # 1. Architecture compliance
            arch_issues = self._validate_architecture(file_path, context)
            issues.extend(arch_issues)
            
            # 2. Naming conventions
            naming_issues = self._validate_naming(file_path)
            issues.extend(naming_issues)
            
            # 3. Documentation quality
            doc_issues = self._validate_documentation(file_path)
            issues.extend(doc_issues)
            
            # 4. Best practices adherence
            best_practice_issues = self._validate_best_practices(file_path, context)
            issues.extend(best_practice_issues)
            
            # 5. Domain-specific validation
            domain_issues = self._validate_domain_context(file_path, context)
            issues.extend(domain_issues)
            
            suggestions = self._generate_contextual_suggestions(issues, context)
            
        except Exception as e:
            logger.error(f"Layer 3 validation error: {e}")
            issues.append(ValidationIssue(
                layer=ValidationLayer.CONTEXTUAL,
                severity="error",
                message=f"Contextual validation failed: {str(e)}",
                auto_fixable=False
            ))
        
        # Calculate score
        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])
        info_count = len([i for i in issues if i.severity == "info"])
        
        if error_count > 0:
            score = 0.3
            result = ValidationResult.FAIL
        elif warning_count > 8:
            score = 0.6
            result = ValidationResult.WARNING
        else:
            score = max(0.7, 1.0 - (warning_count * 0.05) - (info_count * 0.02))
            result = ValidationResult.PASS
        
        duration_ms = (time.time() - start_time) * 1000
        
        return LayerValidationResult(
            layer=ValidationLayer.CONTEXTUAL,
            result=result,
            score=score,
            duration_ms=duration_ms,
            issues=issues,
            metrics=metrics,
            suggestions=suggestions
        )
    
    def _validate_architecture(self, file_path: Path, context: WeaverGenerationContext) -> List[ValidationIssue]:
        """Validate architectural patterns"""
        issues = []
        
        if file_path.suffix == ".py":
            content = file_path.read_text()
            
            # Check for appropriate patterns based on feature type
            if "model" in context.feature_name.lower():
                if "from pydantic import" not in content and "BaseModel" not in content:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.CONTEXTUAL,
                        severity="warning",
                        message="Model feature should use Pydantic BaseModel",
                        suggestion="Import and inherit from Pydantic BaseModel",
                        auto_fixable=False
                    ))
            
            if "api" in context.feature_name.lower():
                if "fastapi" not in content.lower() and "flask" not in content.lower():
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.CONTEXTUAL,
                        severity="info",
                        message="API feature might benefit from FastAPI or Flask",
                        suggestion="Consider using a web framework",
                        auto_fixable=False
                    ))
        
        return issues
    
    def _validate_naming(self, file_path: Path) -> List[ValidationIssue]:
        """Validate naming conventions"""
        issues = []
        
        if file_path.suffix == ".py":
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Class names should be PascalCase
                        if not node.name[0].isupper():
                            issues.append(ValidationIssue(
                                layer=ValidationLayer.CONTEXTUAL,
                                severity="warning",
                                message=f"Class name should be PascalCase: {node.name}",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                suggestion=f"Rename to {node.name.title()}",
                                auto_fixable=True
                            ))
                    
                    elif isinstance(node, ast.FunctionDef):
                        # Function names should be snake_case
                        if any(c.isupper() for c in node.name):
                            issues.append(ValidationIssue(
                                layer=ValidationLayer.CONTEXTUAL,
                                severity="warning",
                                message=f"Function name should be snake_case: {node.name}",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                suggestion=f"Rename to {self._to_snake_case(node.name)}",
                                auto_fixable=True
                            ))
                            
            except Exception as e:
                logger.warning(f"Naming validation failed: {e}")
        
        return issues
    
    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case"""
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    
    def _validate_documentation(self, file_path: Path) -> List[ValidationIssue]:
        """Validate documentation quality"""
        issues = []
        
        if file_path.suffix == ".py":
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                # Check for module docstring
                if not ast.get_docstring(tree):
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.CONTEXTUAL,
                        severity="info",
                        message="Missing module docstring",
                        file_path=str(file_path),
                        line_number=1,
                        suggestion="Add module-level docstring",
                        auto_fixable=False
                    ))
                
                # Check for class and function docstrings
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        if not ast.get_docstring(node):
                            issues.append(ValidationIssue(
                                layer=ValidationLayer.CONTEXTUAL,
                                severity="info",
                                message=f"Missing docstring for {node.name}",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                suggestion=f"Add docstring for {node.name}",
                                auto_fixable=False
                            ))
                            
            except Exception as e:
                logger.warning(f"Documentation validation failed: {e}")
        
        return issues
    
    def _validate_best_practices(self, file_path: Path, context: WeaverGenerationContext) -> List[ValidationIssue]:
        """Validate coding best practices"""
        issues = []
        
        if file_path.suffix == ".py":
            content = file_path.read_text()
            
            # Check for magic numbers
            numbers = re.findall(r'\b\d{2,}\b', content)
            if len(numbers) > 5:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.CONTEXTUAL,
                    severity="info",
                    message="Consider using named constants instead of magic numbers",
                    suggestion="Define constants for numeric values",
                    auto_fixable=False
                ))
            
            # Check for exception handling
            if "try:" in content and "except Exception:" in content:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.CONTEXTUAL,
                    severity="warning",
                    message="Avoid catching generic Exception",
                    suggestion="Catch specific exception types",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_domain_context(self, file_path: Path, context: WeaverGenerationContext) -> List[ValidationIssue]:
        """Validate domain-specific requirements"""
        issues = []
        
        # Domain-specific validation based on semantic model
        if context.semantic_model == "openapi":
            content = file_path.read_text()
            if "response_model" not in content:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.CONTEXTUAL,
                    severity="info",
                    message="OpenAPI endpoints should specify response models",
                    suggestion="Add response_model parameter",
                    auto_fixable=False
                ))
        
        return issues
    
    def _generate_contextual_suggestions(self, issues: List[ValidationIssue], context: WeaverGenerationContext) -> List[str]:
        """Generate contextual improvement suggestions"""
        suggestions = []
        
        naming_issues = len([i for i in issues if "name" in i.message.lower()])
        doc_issues = len([i for i in issues if "docstring" in i.message.lower()])
        
        if naming_issues > 3:
            suggestions.append("Improve naming convention consistency in weaver templates")
        
        if doc_issues > 5:
            suggestions.append("Add documentation generation to weaver spec")
            suggestions.append("Use more descriptive semantic models")
        
        return suggestions


class Layer4IntegrationValidator:
    """Layer 4: Integration and performance validation"""
    
    def __init__(self):
        self.name = "Integration Validator"
    
    async def validate(self, file_path: Path, context: WeaverGenerationContext) -> LayerValidationResult:
        """Validate integration and performance aspects"""
        start_time = time.time()
        issues = []
        metrics = {}
        suggestions = []
        
        try:
            # 1. Import resolution
            import_issues = await self._validate_imports(file_path)
            issues.extend(import_issues)
            
            # 2. Performance analysis
            perf_metrics = await self._analyze_performance(file_path)
            metrics.update(perf_metrics)
            
            # 3. Memory usage analysis
            memory_issues = self._analyze_memory_usage(file_path)
            issues.extend(memory_issues)
            
            # 4. Integration compatibility
            integration_issues = self._validate_integration(file_path, context)
            issues.extend(integration_issues)
            
            suggestions = self._generate_integration_suggestions(issues, metrics, context)
            
        except Exception as e:
            logger.error(f"Layer 4 validation error: {e}")
            issues.append(ValidationIssue(
                layer=ValidationLayer.INTEGRATION,
                severity="error",
                message=f"Integration validation failed: {str(e)}",
                auto_fixable=False
            ))
        
        # Calculate score based on integration health
        error_count = len([i for i in issues if i.severity == "error"])
        performance_score = metrics.get("performance_score", 0.5)
        
        if error_count > 0:
            score = 0.2
            result = ValidationResult.FAIL
        elif performance_score < 0.3:
            score = 0.4
            result = ValidationResult.WARNING
        else:
            score = min(0.9, performance_score * 1.2)
            result = ValidationResult.PASS
        
        duration_ms = (time.time() - start_time) * 1000
        
        return LayerValidationResult(
            layer=ValidationLayer.INTEGRATION,
            result=result,
            score=score,
            duration_ms=duration_ms,
            issues=issues,
            metrics=metrics,
            suggestions=suggestions
        )
    
    async def _validate_imports(self, file_path: Path) -> List[ValidationIssue]:
        """Validate that all imports can be resolved"""
        issues = []
        
        if file_path.suffix == ".py":
            try:
                # Try to import the module
                import_name = file_path.stem
                spec = None
                
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(import_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                except Exception as e:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.INTEGRATION,
                        severity="error",
                        message=f"Import error: {str(e)}",
                        file_path=str(file_path),
                        suggestion="Fix import dependencies",
                        auto_fixable=False
                    ))
                    
            except Exception as e:
                logger.warning(f"Import validation failed: {e}")
        
        return issues
    
    async def _analyze_performance(self, file_path: Path) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        metrics = {"performance_score": 0.5}
        
        try:
            if file_path.suffix == ".py":
                content = file_path.read_text()
                
                # Simple performance heuristics
                lines_of_code = len(content.split('\n'))
                metrics["lines_of_code"] = lines_of_code
                
                # Nested loop detection
                nested_loops = content.count('for') * content.count('while')
                if nested_loops > 10:
                    metrics["performance_score"] *= 0.8
                
                # Large string operations
                if content.count('+') > 20:  # String concatenation
                    metrics["performance_score"] *= 0.9
                
                # Function count (complexity indicator)
                function_count = content.count('def ')
                metrics["function_count"] = function_count
                
                if function_count > 20:
                    metrics["performance_score"] *= 0.9
                
                # Final normalization
                metrics["performance_score"] = min(1.0, max(0.1, metrics["performance_score"]))
                
        except Exception as e:
            logger.warning(f"Performance analysis failed: {e}")
        
        return metrics
    
    def _analyze_memory_usage(self, file_path: Path) -> List[ValidationIssue]:
        """Analyze potential memory issues"""
        issues = []
        
        if file_path.suffix == ".py":
            content = file_path.read_text()
            
            # Check for potential memory leaks
            if "while True:" in content and "break" not in content:
                issues.append(ValidationIssue(
                    layer=ValidationLayer.INTEGRATION,
                    severity="warning",
                    message="Potential infinite loop without break condition",
                    suggestion="Add break condition or timeout",
                    auto_fixable=False
                ))
            
            # Large data structure warnings
            if re.search(r'\[\s*.*\s*for.*in.*\]', content):  # List comprehensions
                if len(content) > 1000:  # In large files
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.INTEGRATION,
                        severity="info",
                        message="Consider generator expressions for memory efficiency",
                        suggestion="Use generators for large data processing",
                        auto_fixable=False
                    ))
        
        return issues
    
    def _validate_integration(self, file_path: Path, context: WeaverGenerationContext) -> List[ValidationIssue]:
        """Validate integration with existing system"""
        issues = []
        
        # Check for DSLModel integration patterns
        if file_path.suffix == ".py":
            content = file_path.read_text()
            
            # Check for proper DSLModel usage
            if "model" in context.feature_name.lower():
                if "DSLModel" not in content and "BaseModel" not in content:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.INTEGRATION,
                        severity="warning",
                        message="Consider using DSLModel or Pydantic BaseModel",
                        suggestion="Inherit from appropriate base model class",
                        auto_fixable=False
                    ))
            
            # Check for OTEL integration
            if "observability" in context.feature_name.lower():
                if "opentelemetry" not in content:
                    issues.append(ValidationIssue(
                        layer=ValidationLayer.INTEGRATION,
                        severity="warning",
                        message="OTEL feature should include OpenTelemetry imports",
                        suggestion="Add OpenTelemetry tracing/metrics",
                        auto_fixable=False
                    ))
        
        return issues
    
    def _generate_integration_suggestions(self, issues: List[ValidationIssue], metrics: Dict[str, Any], context: WeaverGenerationContext) -> List[str]:
        """Generate integration improvement suggestions"""
        suggestions = []
        
        performance_score = metrics.get("performance_score", 0.5)
        if performance_score < 0.5:
            suggestions.append("Optimize performance-critical code paths")
            suggestions.append("Consider async/await patterns for I/O operations")
        
        import_errors = len([i for i in issues if "import" in i.message.lower()])
        if import_errors > 0:
            suggestions.append("Review and fix dependency issues")
            suggestions.append("Add missing packages to requirements")
        
        return suggestions


class MultiLayerWeaverValidator:
    """Main orchestrator for multi-layer validation with feedback"""
    
    def __init__(self):
        self.layer1 = Layer1SyntaxValidator()
        self.layer2 = Layer2SemanticValidator()
        self.layer3 = Layer3ContextualValidator()
        self.layer4 = Layer4IntegrationValidator()
        
        self.feedback_history: List[ValidationFeedback] = []
    
    async def validate_all_layers(self, file_path: Path, context: WeaverGenerationContext) -> Tuple[Dict[ValidationLayer, LayerValidationResult], ValidationFeedback]:
        """Run all validation layers and generate feedback"""
        console.print(f"🔍 Running multi-layer validation on {file_path.name}")
        
        results = {}
        
        # Layer 1: Syntax
        console.print("  📝 Layer 1: Syntax & Structure...")
        results[ValidationLayer.SYNTAX] = await self.layer1.validate(file_path, context)
        
        # Layer 2: Semantic (only if syntax passes)
        if results[ValidationLayer.SYNTAX].result != ValidationResult.FAIL:
            console.print("  🧠 Layer 2: Semantic & Behavioral...")
            results[ValidationLayer.SEMANTIC] = await self.layer2.validate(file_path, context)
        else:
            console.print("  ⏭️  Layer 2: Skipped (syntax errors)")
            results[ValidationLayer.SEMANTIC] = LayerValidationResult(
                layer=ValidationLayer.SEMANTIC,
                result=ValidationResult.SKIP,
                score=0.0,
                duration_ms=0.0
            )
        
        # Layer 3: Contextual (only if semantic passes)
        if results[ValidationLayer.SEMANTIC].result != ValidationResult.FAIL:
            console.print("  🎯 Layer 3: Contextual & Quality...")
            results[ValidationLayer.CONTEXTUAL] = await self.layer3.validate(file_path, context)
        else:
            console.print("  ⏭️  Layer 3: Skipped (semantic errors)")
            results[ValidationLayer.CONTEXTUAL] = LayerValidationResult(
                layer=ValidationLayer.CONTEXTUAL,
                result=ValidationResult.SKIP,
                score=0.0,
                duration_ms=0.0
            )
        
        # Layer 4: Integration (only if contextual passes)
        if results[ValidationLayer.CONTEXTUAL].result != ValidationResult.FAIL:
            console.print("  🔗 Layer 4: Integration & Performance...")
            results[ValidationLayer.INTEGRATION] = await self.layer4.validate(file_path, context)
        else:
            console.print("  ⏭️  Layer 4: Skipped (contextual errors)")
            results[ValidationLayer.INTEGRATION] = LayerValidationResult(
                layer=ValidationLayer.INTEGRATION,
                result=ValidationResult.SKIP,
                score=0.0,
                duration_ms=0.0
            )
        
        # Generate feedback
        feedback = self._generate_feedback(results, context)
        self.feedback_history.append(feedback)
        
        return results, feedback
    
    def _generate_feedback(self, results: Dict[ValidationLayer, LayerValidationResult], context: WeaverGenerationContext) -> ValidationFeedback:
        """Generate comprehensive feedback for weaver improvement"""
        
        # Calculate overall score (weighted)
        weights = {
            ValidationLayer.SYNTAX: 0.3,
            ValidationLayer.SEMANTIC: 0.4,
            ValidationLayer.CONTEXTUAL: 0.2,
            ValidationLayer.INTEGRATION: 0.1
        }
        
        overall_score = 0.0
        layer_scores = {}
        
        for layer, result in results.items():
            layer_scores[layer] = result.score
            overall_score += result.score * weights[layer]
        
        # Collect common issues
        all_issues = []
        for result in results.values():
            all_issues.extend(result.issues)
        
        issue_patterns = {}
        for issue in all_issues:
            key = issue.message.split(':')[0]  # First part of message
            issue_patterns[key] = issue_patterns.get(key, 0) + 1
        
        common_issues = [k for k, v in issue_patterns.items() if v >= 2]
        
        # Generate improvement suggestions
        improvement_suggestions = []
        parameter_adjustments = {}
        model_recommendations = []
        
        # Based on layer performance
        if layer_scores.get(ValidationLayer.SYNTAX, 0) < 0.5:
            improvement_suggestions.append("Focus on syntax and structure quality")
            parameter_adjustments["syntax_strictness"] = "high"
            
        if layer_scores.get(ValidationLayer.SEMANTIC, 0) < 0.5:
            improvement_suggestions.append("Improve semantic model specificity")
            parameter_adjustments["test_coverage"] = "required"
            model_recommendations.append("Use more domain-specific models")
            
        if layer_scores.get(ValidationLayer.CONTEXTUAL, 0) < 0.5:
            improvement_suggestions.append("Add contextual constraints to weaver spec")
            parameter_adjustments["naming_convention"] = "strict"
            
        if layer_scores.get(ValidationLayer.INTEGRATION, 0) < 0.5:
            improvement_suggestions.append("Improve integration patterns")
            parameter_adjustments["dependency_validation"] = "required"
        
        # Based on attempt history
        if context.previous_attempts > 2:
            improvement_suggestions.append("Consider simpler semantic model")
            parameter_adjustments["complexity_limit"] = "medium"
        
        return ValidationFeedback(
            overall_score=overall_score,
            layer_scores=layer_scores,
            common_issues=common_issues,
            improvement_suggestions=improvement_suggestions,
            parameter_adjustments=parameter_adjustments,
            model_recommendations=model_recommendations
        )
    
    def display_results(self, results: Dict[ValidationLayer, LayerValidationResult], feedback: ValidationFeedback):
        """Display validation results and feedback"""
        
        # Results table
        table = Table(title="🔍 Multi-Layer Validation Results")
        table.add_column("Layer", style="cyan")
        table.add_column("Result", style="bold")
        table.add_column("Score", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Issues", style="red")
        
        for layer, result in results.items():
            result_style = "green" if result.result == ValidationResult.PASS else "red" if result.result == ValidationResult.FAIL else "yellow"
            
            table.add_row(
                layer.value.title(),
                f"[{result_style}]{result.result.value.upper()}[/{result_style}]",
                f"{result.score:.2f}",
                f"{result.duration_ms:.0f}ms",
                str(len(result.issues))
            )
        
        console.print(table)
        
        # Feedback panel
        feedback_text = f"""
📊 **Overall Score**: {feedback.overall_score:.2f}/1.0

🔧 **Improvement Suggestions**:
{chr(10).join(f"  • {s}" for s in feedback.improvement_suggestions)}

⚙️ **Parameter Adjustments**:
{chr(10).join(f"  • {k}: {v}" for k, v in feedback.parameter_adjustments.items())}

🤖 **Model Recommendations**:
{chr(10).join(f"  • {r}" for r in feedback.model_recommendations)}
"""
        
        console.print(Panel(
            feedback_text,
            title="📈 Feedback for Weaver Improvement",
            border_style="blue"
        ))
    
    def get_historical_trends(self) -> Dict[str, Any]:
        """Analyze historical feedback trends"""
        if not self.feedback_history:
            return {"message": "No historical data available"}
        
        scores = [f.overall_score for f in self.feedback_history]
        
        return {
            "total_validations": len(self.feedback_history),
            "average_score": sum(scores) / len(scores),
            "improvement_trend": scores[-1] - scores[0] if len(scores) > 1 else 0,
            "common_issues_frequency": self._analyze_issue_patterns(),
            "best_performing_layers": self._find_best_layers(),
            "recommendations_applied": self._track_recommendation_adoption()
        }
    
    def _analyze_issue_patterns(self) -> Dict[str, int]:
        """Analyze patterns in common issues"""
        all_issues = []
        for feedback in self.feedback_history:
            all_issues.extend(feedback.common_issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        return dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _find_best_layers(self) -> List[str]:
        """Find consistently best performing layers"""
        layer_averages = {}
        
        for feedback in self.feedback_history:
            for layer, score in feedback.layer_scores.items():
                if layer not in layer_averages:
                    layer_averages[layer] = []
                layer_averages[layer].append(score)
        
        # Calculate averages
        layer_performance = {}
        for layer, scores in layer_averages.items():
            layer_performance[layer.value] = sum(scores) / len(scores)
        
        return sorted(layer_performance.keys(), key=lambda x: layer_performance[x], reverse=True)
    
    def _track_recommendation_adoption(self) -> Dict[str, int]:
        """Track how often recommendations are applied"""
        # Simplified tracking - in practice, would compare across generations
        rec_counts = {}
        
        for feedback in self.feedback_history:
            for rec in feedback.improvement_suggestions:
                rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        return rec_counts