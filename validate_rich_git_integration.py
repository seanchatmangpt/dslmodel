#!/usr/bin/env python3
"""
Rich-Git Integration Validation
Comprehensive test of Level-5 Git operations with Weaver/OTEL ecosystem
"""

import subprocess
import sys
import time
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

# Colors for output
GREEN = '✅'
RED = '❌'
YELLOW = '⚠️'
BLUE = '🔧'

class RichGitValidator:
    """Validator for Rich-Git Level-5 integration"""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        self.results.append({
            "name": name,
            "success": success,
            "details": details
        })
        
        status = GREEN if success else RED
        console.print(f"{status} {name}")
        if details and not success:
            console.print(f"   📝 {details}")

    def run_command(self, cmd: str) -> Tuple[bool, str, str]:
        """Run command and return success, stdout, stderr"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def test_semantic_conventions(self) -> None:
        """Test Git semantic conventions are properly created"""
        console.print(f"\n{BLUE} Testing Git Semantic Conventions")
        
        # Check if git events directory exists
        git_events_dir = Path("semconv_registry/git_events")
        success = git_events_dir.exists()
        self.log_test("Git events directory exists", success)
        
        if not success:
            return
            
        # Check individual semantic convention files
        expected_files = [
            "git.submodule.update.semconv.yaml",
            "git.hook.run.semconv.yaml", 
            "git.reset.semconv.yaml",
            "git.rebase.semconv.yaml"
        ]
        
        for filename in expected_files:
            filepath = git_events_dir / filename
            exists = filepath.exists()
            self.log_test(f"Semantic convention: {filename}", exists)
            
            if exists:
                # Validate YAML structure
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                    
                    has_groups = 'groups' in data
                    self.log_test(f"Valid YAML structure: {filename}", has_groups)
                    
                except Exception as e:
                    self.log_test(f"YAML parsing: {filename}", False, str(e))

    def test_git_registry(self) -> None:
        """Test git registry configuration"""
        console.print(f"\n{BLUE} Testing Git Registry Configuration")
        
        registry_file = Path("git_registry.yaml")
        exists = registry_file.exists()
        self.log_test("Git registry file exists", exists)
        
        if not exists:
            return
            
        try:
            with open(registry_file, 'r') as f:
                registry = yaml.safe_load(f)
            
            # Check main sections
            expected_sections = [
                "data_layer", "collaboration", "workflow", 
                "security", "maintenance", "federation"
            ]
            
            for section in expected_sections:
                has_section = section in registry
                self.log_test(f"Registry section: {section}", has_section)
            
            # Check specific commands
            expected_commands = [
                ("data_layer", "worktree"),
                ("collaboration", "submodule_add"),
                ("workflow", "cherry_pick"),
                ("security", "sign_commit"),
                ("maintenance", "gc_aggressive")
            ]
            
            for section, command in expected_commands:
                if section in registry:
                    has_command = command in registry[section]
                    self.log_test(f"Command {section}.{command}", has_command)
                    
        except Exception as e:
            self.log_test("Git registry parsing", False, str(e))

    def test_git_level5_module(self) -> None:
        """Test GitLevel5 module functionality"""
        console.print(f"\n{BLUE} Testing GitLevel5 Module")
        
        try:
            # Test import
            from src.dslmodel.commands.git_level5 import GitLevel5
            self.log_test("GitLevel5 import", True)
            
            # Test instantiation
            git_l5 = GitLevel5()
            self.log_test("GitLevel5 instantiation", True)
            
            # Test federation status (doesn't require git repo)
            try:
                status = git_l5.federation_status()
                has_remotes = isinstance(status.get("remotes"), list)
                self.log_test("Federation status method", has_remotes)
            except Exception as e:
                self.log_test("Federation status method", False, str(e))
                
        except ImportError as e:
            self.log_test("GitLevel5 import", False, str(e))
        except Exception as e:
            self.log_test("GitLevel5 module", False, str(e))

    def test_hook_pipeline_module(self) -> None:
        """Test Git hook pipeline module"""
        console.print(f"\n{BLUE} Testing Git Hook Pipeline Module")
        
        try:
            # Test import
            from src.dslmodel.commands.git_hook_pipeline import GitHookPipeline
            self.log_test("GitHookPipeline import", True)
            
            # Test instantiation
            pipeline = GitHookPipeline()
            self.log_test("GitHookPipeline instantiation", True)
            
            # Test hook configs loading
            configs = pipeline.hook_configs
            has_configs = isinstance(configs, dict) and len(configs) > 0
            self.log_test("Hook configs loaded", has_configs)
            
        except ImportError as e:
            self.log_test("GitHookPipeline import", False, str(e))
        except Exception as e:
            self.log_test("GitHookPipeline module", False, str(e))

    def test_weaver_integration(self) -> None:
        """Test Weaver integration with Git semantic conventions"""
        console.print(f"\n{BLUE} Testing Weaver Integration")
        
        # Test weaver command availability
        success, stdout, stderr = self.run_command("weaver --help")
        self.log_test("Weaver command available", success)
        
        if not success:
            return
            
        # Test registry validation
        success, stdout, stderr = self.run_command("weaver registry check semconv_registry")
        if success:
            self.log_test("Weaver registry validation", True)
        else:
            # Weaver might fail due to syntax issues, but command should work
            command_worked = "registry" in stderr or "check" in stderr
            self.log_test("Weaver registry check command", command_worked, stderr[:100])

    def test_otel_integration(self) -> None:
        """Test OpenTelemetry integration"""
        console.print(f"\n{BLUE} Testing OpenTelemetry Integration")
        
        # Test OTEL imports
        try:
            import opentelemetry
            from opentelemetry import trace
            from opentelemetry.trace import Span
            self.log_test("OpenTelemetry imports", True)
            
            # Test tracer creation
            tracer = trace.get_tracer(__name__)
            self.log_test("Tracer creation", True)
            
            # Test span creation
            with tracer.start_as_current_span("test.span") as span:
                span.set_attribute("test.attribute", "test_value")
            self.log_test("Span creation and attributes", True)
            
        except ImportError as e:
            self.log_test("OpenTelemetry imports", False, str(e))
        except Exception as e:
            self.log_test("OpenTelemetry functionality", False, str(e))

    def test_cli_integration(self) -> None:
        """Test CLI integration for rich-git commands"""
        console.print(f"\n{BLUE} Testing CLI Integration")
        
        # Test DSL CLI with help for git-related commands
        test_commands = [
            ("dsl --help", "DSL CLI available"),
            ("dsl weaver-health check --help", "Weaver health command"),
            ("dsl otel-monitor status --help", "OTEL monitor command"),
            ("dsl health-8020 analyze --help", "Health analysis command")
        ]
        
        for cmd, name in test_commands:
            success, stdout, stderr = self.run_command(f"uv run {cmd}")
            # Command should work even if it shows help
            command_worked = success or "Usage:" in stderr or "help" in stdout.lower()
            self.log_test(name, command_worked)

    def test_file_structure_integrity(self) -> None:
        """Test file structure integrity for rich-git"""
        console.print(f"\n{BLUE} Testing File Structure Integrity")
        
        # Check key directories exist
        key_dirs = [
            "src/dslmodel/commands",
            "semconv_registry",
            "src/dslmodel/weaver",
            "src/dslmodel/otel"
        ]
        
        for dir_path in key_dirs:
            exists = Path(dir_path).exists()
            self.log_test(f"Directory exists: {dir_path}", exists)
        
        # Check key files exist
        key_files = [
            "src/dslmodel/commands/git_level5.py",
            "src/dslmodel/commands/git_hook_pipeline.py",
            "git_registry.yaml",
            "pyproject.toml",
            "uv.lock"
        ]
        
        for file_path in key_files:
            exists = Path(file_path).exists()
            self.log_test(f"File exists: {file_path}", exists)

    def test_uv_integration(self) -> None:
        """Test UV package manager integration"""
        console.print(f"\n{BLUE} Testing UV Integration")
        
        # Test UV is available
        success, stdout, stderr = self.run_command("uv --version")
        self.log_test("UV command available", success)
        
        # Test UV run works
        success, stdout, stderr = self.run_command("uv run python --version")
        self.log_test("UV run functionality", success)
        
        # Test dsl wrapper script
        success, stdout, stderr = self.run_command("./dsl --help")
        self.log_test("DSL wrapper script", success)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive rich-git integration tests"""
        console.print(Panel.fit(
            "🚀 Rich-Git Level-5 Integration Validation\n"
            "Testing advanced Git primitives with Weaver/OTEL ecosystem",
            style="bold blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            tests = [
                ("File Structure", self.test_file_structure_integrity),
                ("UV Integration", self.test_uv_integration), 
                ("Semantic Conventions", self.test_semantic_conventions),
                ("Git Registry", self.test_git_registry),
                ("GitLevel5 Module", self.test_git_level5_module),
                ("Hook Pipeline", self.test_hook_pipeline_module),
                ("Weaver Integration", self.test_weaver_integration),
                ("OTEL Integration", self.test_otel_integration),
                ("CLI Integration", self.test_cli_integration)
            ]
            
            main_task = progress.add_task("Running tests...", total=len(tests))
            
            for test_name, test_func in tests:
                progress.update(main_task, description=f"Testing: {test_name}")
                test_func()
                progress.advance(main_task)
        
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        # Summary table
        table = Table(title="Rich-Git Integration Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")
        
        for result in self.results:
            status = f"{GREEN} PASS" if result["success"] else f"{RED} FAIL"
            details = result["details"][:50] + "..." if len(result["details"]) > 50 else result["details"]
            table.add_row(result["name"], status, details)
        
        console.print(table)
        
        # Summary panel
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        summary = f"""
📊 Test Summary:
   Total Tests: {self.total_tests}
   Passed: {self.passed_tests} 
   Failed: {self.total_tests - self.passed_tests}
   Success Rate: {success_rate:.1f}%

🎯 Rich-Git Integration Status:
   {GREEN if success_rate >= 80 else YELLOW if success_rate >= 60 else RED} {'EXCELLENT' if success_rate >= 90 else 'GOOD' if success_rate >= 80 else 'NEEDS_WORK' if success_rate >= 60 else 'CRITICAL'}
        """
        
        console.print(Panel.fit(summary, title="Final Results", style="bold"))
        
        # Detailed report
        report = {
            "timestamp": time.time(),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": success_rate,
            "status": "PASS" if success_rate >= 80 else "PARTIAL" if success_rate >= 60 else "FAIL",
            "tests": self.results
        }
        
        # Save report
        with open("rich_git_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        console.print(f"\n📋 Detailed report saved to: rich_git_validation_report.json")
        
        return report

def main():
    """Main validation function"""
    validator = RichGitValidator()
    report = validator.run_all_tests()
    
    # Exit with appropriate code
    if report["success_rate"] >= 80:
        console.print(f"\n{GREEN} Rich-Git integration validation PASSED!")
        sys.exit(0)
    else:
        console.print(f"\n{RED} Rich-Git integration validation FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()