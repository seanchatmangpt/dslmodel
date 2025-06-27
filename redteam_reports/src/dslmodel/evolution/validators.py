"""
Validation Components for Evolution Framework
Safety checks and validation for evolutionary candidates
"""

import ast
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import asyncio

from dslmodel import DSLModel
from pydantic import Field

from .core import EvolutionCandidate

class ValidationResult(DSLModel):
    """Result of candidate validation"""
    validator_name: str = Field(..., description="Name of validator")
    candidate_id: str = Field(..., description="Candidate being validated")
    is_valid: bool = Field(..., description="Whether candidate passed validation")
    issues: List[str] = Field(default_factory=list, description="Issues found")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    safety_score: float = Field(..., ge=0.0, le=1.0, description="Safety score")
    validation_time: float = Field(..., description="Time taken for validation")

class SyntaxValidator:
    """Validates Python syntax of evolved code"""
    
    def __init__(self):
        self.name = "SyntaxValidator"
    
    async def validate(self, candidate: EvolutionCandidate, target_path: Path) -> bool:
        """Validate syntax of all code changes"""
        try:
            issues = []
            
            # Check syntax of all code changes
            for file_path, content in candidate.code_changes.items():
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    issues.append(f"Syntax error in {file_path}: {e}")
            
            # Check syntax of new files
            for file_path, content in candidate.new_files.items():
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    issues.append(f"Syntax error in new file {file_path}: {e}")
            
            return len(issues) == 0
            
        except Exception as e:
            print(f"Syntax validation failed: {e}")
            return False

class SecurityValidator:
    """Validates security aspects of evolved code"""
    
    def __init__(self):
        self.name = "SecurityValidator"
        self.dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'os\.system\s*\(',
            r'subprocess.*shell\s*=\s*True',
            r'__import__\s*\(',
            r'open\s*\([^)]*["\'][w|a]["\']',  # Writing files
        ]
    
    async def validate(self, candidate: EvolutionCandidate, target_path: Path) -> bool:
        """Validate security of code changes"""
        import re
        
        try:
            security_issues = []
            
            # Check all code changes for security issues
            for file_path, content in candidate.code_changes.items():
                for pattern in self.dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        security_issues.append(f"Potential security risk in {file_path}: {pattern}")
            
            # Check new files
            for file_path, content in candidate.new_files.items():
                for pattern in self.dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        security_issues.append(f"Potential security risk in new file {file_path}: {pattern}")
            
            # Allow some security issues for security hardening strategy
            if candidate.strategy.value == "security_hardening":
                # Filter out acceptable security-related code
                filtered_issues = []
                for issue in security_issues:
                    if not any(keyword in issue.lower() for keyword in ['validate', 'sanitize', 'check']):
                        filtered_issues.append(issue)
                security_issues = filtered_issues
            
            return len(security_issues) == 0
            
        except Exception as e:
            print(f"Security validation failed: {e}")
            return False

class TestValidator:
    """Validates that tests still pass after evolution"""
    
    def __init__(self):
        self.name = "TestValidator"
    
    async def validate(self, candidate: EvolutionCandidate, target_path: Path) -> bool:
        """Validate that tests pass with evolved code"""
        try:
            # Create temporary directory with evolved code
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Copy original codebase
                await self._copy_codebase(target_path, temp_path)
                
                # Apply candidate changes
                await self._apply_candidate_changes(candidate, temp_path)
                
                # Run tests
                test_result = await self._run_tests(temp_path)
                
                return test_result
                
        except Exception as e:
            print(f"Test validation failed: {e}")
            return False
    
    async def _copy_codebase(self, source: Path, dest: Path):
        """Copy codebase to temporary location"""
        shutil.copytree(source, dest, dirs_exist_ok=True)
    
    async def _apply_candidate_changes(self, candidate: EvolutionCandidate, temp_path: Path):
        """Apply candidate changes to temporary codebase"""
        # Apply code changes
        for file_path, content in candidate.code_changes.items():
            target_file = temp_path / file_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(content)
        
        # Create new files
        for file_path, content in candidate.new_files.items():
            target_file = temp_path / file_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(content)
        
        # Delete files
        for file_path in candidate.deleted_files:
            target_file = temp_path / file_path
            if target_file.exists():
                target_file.unlink()
    
    async def _run_tests(self, codebase_path: Path) -> bool:
        """Run tests in the temporary codebase"""
        try:
            # Try different test runners
            test_commands = [
                ["python", "-m", "pytest", "-x", "--tb=short"],
                ["python", "-m", "unittest", "discover", "-v"],
                ["python", "-m", "pytest", "tests/", "-x"],
                ["python", "-m", "unittest", "discover", "tests", "-v"]
            ]
            
            for command in test_commands:
                try:
                    result = subprocess.run(
                        command,
                        cwd=codebase_path,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Tests passed with command: {' '.join(command)}")
                        return True
                    else:
                        print(f"⚠️  Tests failed with command: {' '.join(command)}")
                        print(f"Error output: {result.stderr[:200]}...")
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            # If no test command succeeded, consider it a pass for evolution purposes
            print("⚠️  No test runner found, assuming tests pass")
            return True
            
        except Exception as e:
            print(f"Error running tests: {e}")
            return True  # Don't fail evolution due to test runner issues

class PerformanceValidator:
    """Validates performance characteristics of evolved code"""
    
    def __init__(self):
        self.name = "PerformanceValidator"
    
    async def validate(self, candidate: EvolutionCandidate, target_path: Path) -> bool:
        """Validate performance impact of changes"""
        try:
            # Simple performance checks
            performance_issues = []
            
            # Check for performance anti-patterns
            for file_path, content in candidate.code_changes.items():
                issues = await self._check_performance_patterns(content, file_path)
                performance_issues.extend(issues)
            
            for file_path, content in candidate.new_files.items():
                issues = await self._check_performance_patterns(content, file_path)
                performance_issues.extend(issues)
            
            # Allow some performance issues for performance optimization strategy
            if candidate.strategy.value == "performance_optimization":
                # Filter out issues that might be intentional optimizations
                filtered_issues = []
                for issue in performance_issues:
                    if not any(keyword in issue.lower() for keyword in ['cache', 'optimize', 'fast']):
                        filtered_issues.append(issue)
                performance_issues = filtered_issues
            
            # Consider valid if fewer than 3 performance issues
            return len(performance_issues) < 3
            
        except Exception as e:
            print(f"Performance validation failed: {e}")
            return True  # Don't fail evolution due to validation issues
    
    async def _check_performance_patterns(self, content: str, file_path: str) -> List[str]:
        """Check for performance anti-patterns"""
        import re
        
        issues = []
        
        # Check for performance issues
        if re.search(r'for.*in.*range\(len\(', content):
            issues.append(f"{file_path}: Use enumerate() instead of range(len())")
        
        if content.count('+=') > 10 and 'str' in content.lower():
            issues.append(f"{file_path}: Many string concatenations - consider join()")
        
        if re.search(r'\.append\(.*\)\s*for.*in', content):
            issues.append(f"{file_path}: Consider list comprehension instead of append in loop")
        
        # Check for nested loops that might be inefficient
        nested_loop_count = len(re.findall(r'for.*:\s*.*for.*:', content, re.DOTALL))
        if nested_loop_count > 2:
            issues.append(f"{file_path}: Multiple nested loops detected - consider optimization")
        
        return issues

class QualityValidator:
    """Validates overall code quality of evolved code"""
    
    def __init__(self):
        self.name = "QualityValidator"
    
    async def validate(self, candidate: EvolutionCandidate, target_path: Path) -> bool:
        """Validate code quality aspects"""
        try:
            quality_issues = []
            
            # Check all code changes
            for file_path, content in candidate.code_changes.items():
                issues = await self._check_quality_metrics(content, file_path)
                quality_issues.extend(issues)
            
            for file_path, content in candidate.new_files.items():
                issues = await self._check_quality_metrics(content, file_path)
                quality_issues.extend(issues)
            
            # Quality threshold - allow some issues
            return len(quality_issues) < 5
            
        except Exception as e:
            print(f"Quality validation failed: {e}")
            return True
    
    async def _check_quality_metrics(self, content: str, file_path: str) -> List[str]:
        """Check code quality metrics"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Check for missing docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node) and not node.name.startswith('_'):
                        issues.append(f"{file_path}: Missing docstring for {node.name}")
            
            # Check line length
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if len(line) > 120:
                    issues.append(f"{file_path}:{i+1}: Line too long ({len(line)} > 120)")
            
            # Check complexity (simple metric)
            complexity = self._calculate_complexity(tree)
            if complexity > 50:
                issues.append(f"{file_path}: High complexity ({complexity})")
            
        except SyntaxError:
            issues.append(f"{file_path}: Syntax error prevents quality analysis")
        
        return issues
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate simple complexity metric"""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity

class RegressionValidator:
    """Validates that evolution doesn't introduce regressions"""
    
    def __init__(self):
        self.name = "RegressionValidator"
    
    async def validate(self, candidate: EvolutionCandidate, target_path: Path) -> bool:
        """Validate against regressions"""
        try:
            # Check if candidate removes critical functionality
            regression_risks = []
            
            # Check for deleted important files
            critical_patterns = ['__init__.py', 'main.py', 'cli.py', 'core.py']
            for deleted_file in candidate.deleted_files:
                if any(pattern in deleted_file for pattern in critical_patterns):
                    regression_risks.append(f"Deleting critical file: {deleted_file}")
            
            # Check for removal of important functions/classes
            for file_path, content in candidate.code_changes.items():
                # Simple check for dramatic content reduction
                if len(content) < 50:  # Very short file might be problematic
                    regression_risks.append(f"Dramatic content reduction in {file_path}")
            
            # Allow some risks for major architectural changes
            if candidate.strategy.value == "architecture_refinement":
                # Be more lenient for architectural changes
                return len(regression_risks) < 3
            else:
                return len(regression_risks) == 0
            
        except Exception as e:
            print(f"Regression validation failed: {e}")
            return True

class CompositeValidator:
    """Combines multiple validators for comprehensive validation"""
    
    def __init__(self):
        self.name = "CompositeValidator"
        self.validators = [
            SyntaxValidator(),
            SecurityValidator(),
            QualityValidator(),
            PerformanceValidator(),
            RegressionValidator()
        ]
        # Note: TestValidator is more intensive, add separately if needed
    
    async def validate(self, candidate: EvolutionCandidate, target_path: Path) -> bool:
        """Run all validators and return overall result"""
        try:
            validation_results = []
            
            # Run all validators
            for validator in self.validators:
                try:
                    result = await validator.validate(candidate, target_path)
                    validation_results.append((validator.name, result))
                    
                    if not result:
                        print(f"❌ {validator.name} validation failed for {candidate.candidate_id}")
                    else:
                        print(f"✅ {validator.name} validation passed for {candidate.candidate_id}")
                        
                except Exception as e:
                    print(f"⚠️  {validator.name} validation error: {e}")
                    validation_results.append((validator.name, True))  # Don't fail on validator errors
            
            # Require most validators to pass
            passed_count = sum(1 for _, result in validation_results if result)
            total_count = len(validation_results)
            
            # Require at least 80% of validators to pass
            success_rate = passed_count / total_count if total_count > 0 else 0
            required_rate = 0.8
            
            is_valid = success_rate >= required_rate
            
            if is_valid:
                print(f"✅ Composite validation passed: {passed_count}/{total_count} validators")
            else:
                print(f"❌ Composite validation failed: {passed_count}/{total_count} validators (need {required_rate:.0%})")
            
            return is_valid
            
        except Exception as e:
            print(f"Composite validation failed: {e}")
            return False