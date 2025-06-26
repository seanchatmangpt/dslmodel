"""
Specialized Security Scanners for DSLModel Components
"""

import re
import ast
import subprocess
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import hashlib
import secrets
from datetime import datetime

from .core import (
    RedTeamScanner, VulnerabilityReport, AttackVector,
    SeverityLevel, AttackType, VulnerabilityCategory
)

class CodeVulnerabilityScanner(RedTeamScanner):
    """Scans Python code for security vulnerabilities"""
    
    def __init__(self, target_path: Path):
        super().__init__("CodeVulnerabilityScanner", target_path)
        self.dangerous_patterns = {
            # Code injection patterns
            r"eval\s*\(": (SeverityLevel.CRITICAL, AttackType.CODE_INJECTION, "eval() usage"),
            r"exec\s*\(": (SeverityLevel.CRITICAL, AttackType.CODE_INJECTION, "exec() usage"),
            r"compile\s*\(": (SeverityLevel.HIGH, AttackType.CODE_INJECTION, "compile() usage"),
            r"__import__\s*\(": (SeverityLevel.MEDIUM, AttackType.CODE_INJECTION, "Dynamic import"),
            
            # Command injection
            r"os\.system\s*\(": (SeverityLevel.CRITICAL, AttackType.CODE_INJECTION, "os.system() usage"),
            r"subprocess\.call\s*\(": (SeverityLevel.HIGH, AttackType.CODE_INJECTION, "subprocess.call() without shell=False"),
            r"subprocess\.run\s*\(.*shell\s*=\s*True": (SeverityLevel.HIGH, AttackType.CODE_INJECTION, "subprocess with shell=True"),
            
            # Crypto issues
            r"hashlib\.md5\s*\(": (SeverityLevel.MEDIUM, AttackType.CRYPTOGRAPHIC, "MD5 usage"),
            r"hashlib\.sha1\s*\(": (SeverityLevel.MEDIUM, AttackType.CRYPTOGRAPHIC, "SHA1 usage"),
            r"random\.random\s*\(": (SeverityLevel.LOW, AttackType.CRYPTOGRAPHIC, "Non-cryptographic random"),
            
            # Hardcoded secrets
            r"password\s*=\s*['\"][^'\"]+['\"]": (SeverityLevel.HIGH, AttackType.AUTHENTICATION_BYPASS, "Hardcoded password"),
            r"api_key\s*=\s*['\"][^'\"]+['\"]": (SeverityLevel.HIGH, AttackType.DATA_EXFILTRATION, "Hardcoded API key"),
            r"secret\s*=\s*['\"][^'\"]+['\"]": (SeverityLevel.HIGH, AttackType.DATA_EXFILTRATION, "Hardcoded secret"),
            
            # SQL injection patterns (if using SQL)
            r"\.execute\s*\(\s*['\"].*%.*['\"]": (SeverityLevel.CRITICAL, AttackType.CODE_INJECTION, "SQL injection via string formatting"),
            r"\.execute\s*\(\s*.*\+.*\)": (SeverityLevel.CRITICAL, AttackType.CODE_INJECTION, "SQL injection via concatenation"),
            
            # Path traversal
            r"open\s*\(\s*.*\+": (SeverityLevel.MEDIUM, AttackType.DATA_EXFILTRATION, "Potential path traversal in file operations"),
            
            # Telemetry leaks
            r"print\s*\(.*password": (SeverityLevel.MEDIUM, AttackType.TELEMETRY_LEAK, "Password in print statement"),
            r"logging\..*\.info\s*\(.*password": (SeverityLevel.MEDIUM, AttackType.TELEMETRY_LEAK, "Password in logs"),
            r"logger\..*\(.*secret": (SeverityLevel.MEDIUM, AttackType.TELEMETRY_LEAK, "Secret in logs"),
        }
    
    async def scan(self) -> List[VulnerabilityReport]:
        """Scan all Python files for vulnerabilities"""
        self.vulnerabilities = []
        
        # Find all Python files
        python_files = list(self.target_path.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.name.startswith('.'):
                continue
                
            try:
                await self._scan_file(py_file)
            except Exception as e:
                # Create vulnerability report for scan failure
                self.vulnerabilities.append(VulnerabilityReport(
                    vulnerability_id=f"scan_error_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                    title=f"Scanner Error in {py_file.name}",
                    description=f"Failed to scan file: {str(e)}",
                    severity=SeverityLevel.INFO,
                    category=VulnerabilityCategory.A09_LOGGING_MONITORING_FAILURES,
                    attack_type=AttackType.CONFIGURATION,
                    affected_components=[str(py_file)],
                    file_path=str(py_file),
                    remediation="Ensure file is valid Python and accessible for scanning"
                ))
        
        # Additional AST-based scanning
        await self._ast_scan(python_files)
        
        return self.vulnerabilities
    
    async def _scan_file(self, file_path: Path):
        """Scan individual file for vulnerabilities"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Skip binary or non-UTF8 files
            return
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, (severity, attack_type, description) in self.dangerous_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    vuln_id = hashlib.md5(f"{file_path}:{line_num}:{pattern}".encode()).hexdigest()[:16]
                    
                    # Determine OWASP category based on attack type
                    category = self._get_owasp_category(attack_type)
                    
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=vuln_id,
                        title=f"{description} in {file_path.name}",
                        description=f"Potentially dangerous pattern found: {description}",
                        severity=severity,
                        category=category,
                        attack_type=attack_type,
                        affected_components=[str(file_path)],
                        file_path=str(file_path),
                        line_number=line_num,
                        exploit_code=line.strip(),
                        remediation=self._get_remediation(attack_type, description),
                        references=["https://owasp.org/www-project-top-ten/"]
                    ))
    
    async def _ast_scan(self, python_files: List[Path]):
        """Perform AST-based analysis for deeper vulnerabilities"""
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Look for dangerous function calls
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        await self._check_function_call(node, py_file)
                        
            except (SyntaxError, UnicodeDecodeError):
                continue
    
    async def _check_function_call(self, node: ast.Call, file_path: Path):
        """Check specific function calls for security issues"""
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        # Check for dangerous functions
        dangerous_funcs = {
            'eval': (SeverityLevel.CRITICAL, "Dynamic code execution via eval()"),
            'exec': (SeverityLevel.CRITICAL, "Dynamic code execution via exec()"),
            'compile': (SeverityLevel.HIGH, "Dynamic compilation of code"),
        }
        
        if func_name in dangerous_funcs:
            severity, description = dangerous_funcs[func_name]
            vuln_id = hashlib.md5(f"{file_path}:{node.lineno}:{func_name}".encode()).hexdigest()[:16]
            
            self.vulnerabilities.append(VulnerabilityReport(
                vulnerability_id=vuln_id,
                title=f"Dangerous Function Call: {func_name}",
                description=description,
                severity=severity,
                category=VulnerabilityCategory.A03_INJECTION,
                attack_type=AttackType.CODE_INJECTION,
                affected_components=[str(file_path)],
                file_path=str(file_path),
                line_number=node.lineno,
                remediation=f"Avoid using {func_name}() or implement strict input validation"
            ))
    
    def _get_owasp_category(self, attack_type: AttackType) -> VulnerabilityCategory:
        """Map attack type to OWASP category"""
        mapping = {
            AttackType.CODE_INJECTION: VulnerabilityCategory.A03_INJECTION,
            AttackType.CRYPTOGRAPHIC: VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES,
            AttackType.TELEMETRY_LEAK: VulnerabilityCategory.A09_LOGGING_MONITORING_FAILURES,
            AttackType.AUTHENTICATION_BYPASS: VulnerabilityCategory.A07_IDENTIFICATION_FAILURES,
            AttackType.AUTHORIZATION_BYPASS: VulnerabilityCategory.A01_BROKEN_ACCESS_CONTROL,
            AttackType.DATA_EXFILTRATION: VulnerabilityCategory.A01_BROKEN_ACCESS_CONTROL,
            AttackType.CONFIGURATION: VulnerabilityCategory.A05_SECURITY_MISCONFIGURATION,
        }
        return mapping.get(attack_type, VulnerabilityCategory.A05_SECURITY_MISCONFIGURATION)
    
    def _get_remediation(self, attack_type: AttackType, description: str) -> str:
        """Get remediation advice for vulnerability"""
        remediation_map = {
            AttackType.CODE_INJECTION: "Use safe alternatives, implement input validation, avoid dynamic code execution",
            AttackType.CRYPTOGRAPHIC: "Use cryptographically secure functions (secrets.SystemRandom, hashlib.sha256+)",
            AttackType.TELEMETRY_LEAK: "Remove sensitive data from logs, use structured logging with field filtering",
            AttackType.AUTHENTICATION_BYPASS: "Use environment variables or secure configuration management for credentials",
            AttackType.DATA_EXFILTRATION: "Use secure credential management, implement least privilege access",
        }
        return remediation_map.get(attack_type, "Review code for security best practices")
    
    def get_attack_vectors(self) -> List[AttackVector]:
        """Get potential attack vectors for code vulnerabilities"""
        vectors = []
        
        if any(v.attack_type == AttackType.CODE_INJECTION for v in self.vulnerabilities):
            vectors.append(AttackVector(
                vector_id="code_injection_vector",
                name="Code Injection via Dynamic Execution",
                attack_type=AttackType.CODE_INJECTION,
                entry_points=["User input to eval()", "File uploads", "API parameters"],
                prerequisites=["Dynamic code execution functions", "Insufficient input validation"],
                impact="Full system compromise, arbitrary code execution",
                likelihood=0.7,
                detection_difficulty=0.4
            ))
        
        if any(v.attack_type == AttackType.CRYPTOGRAPHIC for v in self.vulnerabilities):
            vectors.append(AttackVector(
                vector_id="crypto_weakness_vector",
                name="Cryptographic Weakness Exploitation",
                attack_type=AttackType.CRYPTOGRAPHIC,
                entry_points=["Hash collision attacks", "Weak random number prediction"],
                prerequisites=["Use of weak cryptographic functions"],
                impact="Data integrity compromise, session hijacking",
                likelihood=0.5,
                detection_difficulty=0.6
            ))
        
        return vectors

class DependencyScanner(RedTeamScanner):
    """Scans dependencies for known vulnerabilities"""
    
    def __init__(self, target_path: Path):
        super().__init__("DependencyScanner", target_path)
        self.known_vulnerable = {
            # Example vulnerable packages and versions
            "requests": {"<2.20.0": SeverityLevel.HIGH},
            "urllib3": {"<1.24.2": SeverityLevel.MEDIUM},
            "jinja2": {"<2.11.3": SeverityLevel.HIGH},
            "pillow": {"<8.1.1": SeverityLevel.CRITICAL},
        }
    
    async def scan(self) -> List[VulnerabilityReport]:
        """Scan dependencies for vulnerabilities"""
        self.vulnerabilities = []
        
        # Check pyproject.toml
        pyproject_path = self.target_path / "pyproject.toml"
        if pyproject_path.exists():
            await self._scan_pyproject(pyproject_path)
        
        # Check requirements.txt
        requirements_path = self.target_path / "requirements.txt"
        if requirements_path.exists():
            await self._scan_requirements(requirements_path)
        
        return self.vulnerabilities
    
    async def _scan_pyproject(self, pyproject_path: Path):
        """Scan pyproject.toml for vulnerable dependencies"""
        try:
            import toml
            content = toml.load(pyproject_path)
            
            dependencies = content.get("tool", {}).get("poetry", {}).get("dependencies", {})
            
            for package, version_spec in dependencies.items():
                if isinstance(version_spec, dict):
                    version_spec = version_spec.get("version", "")
                
                await self._check_package_vulnerability(package, version_spec, str(pyproject_path))
                
        except Exception as e:
            self.vulnerabilities.append(VulnerabilityReport(
                vulnerability_id=f"pyproject_scan_error",
                title="Failed to scan pyproject.toml",
                description=f"Error scanning dependencies: {str(e)}",
                severity=SeverityLevel.INFO,
                category=VulnerabilityCategory.A06_VULNERABLE_COMPONENTS,
                attack_type=AttackType.SUPPLY_CHAIN,
                affected_components=[str(pyproject_path)],
                remediation="Ensure pyproject.toml is valid TOML format"
            ))
    
    async def _scan_requirements(self, requirements_path: Path):
        """Scan requirements.txt for vulnerable dependencies"""
        try:
            content = requirements_path.read_text()
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package==version format
                    if '==' in line:
                        package, version = line.split('==', 1)
                        await self._check_package_vulnerability(package.strip(), f"=={version.strip()}", str(requirements_path))
                        
        except Exception as e:
            self.vulnerabilities.append(VulnerabilityReport(
                vulnerability_id=f"requirements_scan_error",
                title="Failed to scan requirements.txt",
                description=f"Error scanning dependencies: {str(e)}",
                severity=SeverityLevel.INFO,
                category=VulnerabilityCategory.A06_VULNERABLE_COMPONENTS,
                attack_type=AttackType.SUPPLY_CHAIN,
                affected_components=[str(requirements_path)],
                remediation="Ensure requirements.txt is properly formatted"
            ))
    
    async def _check_package_vulnerability(self, package: str, version_spec: str, file_path: str):
        """Check if package version is vulnerable"""
        if package in self.known_vulnerable:
            for vulnerable_range, severity in self.known_vulnerable[package].items():
                # Simplified version checking - in production would use proper version parsing
                vuln_id = hashlib.md5(f"{package}:{version_spec}".encode()).hexdigest()[:16]
                
                self.vulnerabilities.append(VulnerabilityReport(
                    vulnerability_id=vuln_id,
                    title=f"Vulnerable Dependency: {package}",
                    description=f"Package {package} version {version_spec} has known vulnerabilities",
                    severity=severity,
                    category=VulnerabilityCategory.A06_VULNERABLE_COMPONENTS,
                    attack_type=AttackType.SUPPLY_CHAIN,
                    affected_components=[package],
                    file_path=file_path,
                    remediation=f"Update {package} to latest secure version",
                    references=[f"https://pypi.org/project/{package}/"]
                ))
    
    def get_attack_vectors(self) -> List[AttackVector]:
        """Get attack vectors for dependency vulnerabilities"""
        return [
            AttackVector(
                vector_id="supply_chain_attack",
                name="Supply Chain Attack via Vulnerable Dependencies",
                attack_type=AttackType.SUPPLY_CHAIN,
                entry_points=["Vulnerable package versions", "Transitive dependencies"],
                prerequisites=["Use of vulnerable packages"],
                impact="Various depending on vulnerability - RCE, data theft, DoS",
                likelihood=0.6,
                detection_difficulty=0.7
            )
        ]

class PQCCryptoScanner(RedTeamScanner):
    """Scanner for Post-Quantum Cryptography implementations"""
    
    def __init__(self, target_path: Path):
        super().__init__("PQCCryptoScanner", target_path)
        
    async def scan(self) -> List[VulnerabilityReport]:
        """Scan PQC implementations for vulnerabilities"""
        self.vulnerabilities = []
        
        pqc_path = self.target_path / "src" / "dslmodel" / "pqc"
        if not pqc_path.exists():
            return self.vulnerabilities
        
        # Check for weak key generation
        await self._check_key_generation(pqc_path)
        
        # Check for side-channel vulnerabilities
        await self._check_side_channels(pqc_path)
        
        # Check for implementation flaws
        await self._check_implementation_flaws(pqc_path)
        
        return self.vulnerabilities
    
    async def _check_key_generation(self, pqc_path: Path):
        """Check key generation for weaknesses"""
        key_gen_files = list(pqc_path.rglob("*key*"))
        
        for file_path in key_gen_files:
            if file_path.suffix == ".py":
                try:
                    content = file_path.read_text()
                    
                    # Check for weak randomness
                    if re.search(r"random\.random", content):
                        self.vulnerabilities.append(VulnerabilityReport(
                            vulnerability_id=f"pqc_weak_random_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}",
                            title="Weak Randomness in PQC Key Generation",
                            description="Using non-cryptographic random number generator for key generation",
                            severity=SeverityLevel.CRITICAL,
                            category=VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES,
                            attack_type=AttackType.CRYPTOGRAPHIC,
                            affected_components=[str(file_path)],
                            file_path=str(file_path),
                            remediation="Use secrets.SystemRandom() or os.urandom() for cryptographic randomness"
                        ))
                    
                    # Check for hardcoded seeds
                    if re.search(r"seed\s*=\s*\d+", content):
                        self.vulnerabilities.append(VulnerabilityReport(
                            vulnerability_id=f"pqc_hardcoded_seed_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}",
                            title="Hardcoded Seed in PQC Implementation",
                            description="Hardcoded seed makes key generation predictable",
                            severity=SeverityLevel.CRITICAL,
                            category=VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES,
                            attack_type=AttackType.CRYPTOGRAPHIC,
                            affected_components=[str(file_path)],
                            file_path=str(file_path),
                            remediation="Use cryptographically secure random seeds"
                        ))
                        
                except Exception:
                    continue
    
    async def _check_side_channels(self, pqc_path: Path):
        """Check for potential side-channel vulnerabilities"""
        for py_file in pqc_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Check for timing attacks
                if re.search(r"time\.time\(\)", content) and ("verify" in content.lower() or "sign" in content.lower()):
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=f"pqc_timing_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                        title="Potential Timing Side-Channel in PQC",
                        description="Timing measurements in cryptographic operations may leak information",
                        severity=SeverityLevel.MEDIUM,
                        category=VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        attack_type=AttackType.CRYPTOGRAPHIC,
                        affected_components=[str(py_file)],
                        file_path=str(py_file),
                        remediation="Use constant-time implementations for cryptographic operations"
                    ))
                    
            except Exception:
                continue
    
    async def _check_implementation_flaws(self, pqc_path: Path):
        """Check for common implementation flaws"""
        for py_file in pqc_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Check for key reuse
                if re.search(r"private_key.*=.*private_key", content):
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=f"pqc_key_reuse_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                        title="Potential Key Reuse in PQC",
                        description="Private key reuse detected - may compromise security",
                        severity=SeverityLevel.HIGH,
                        category=VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        attack_type=AttackType.CRYPTOGRAPHIC,
                        affected_components=[str(py_file)],
                        file_path=str(py_file),
                        remediation="Ensure each cryptographic operation uses unique keys"
                    ))
                    
            except Exception:
                continue
    
    def get_attack_vectors(self) -> List[AttackVector]:
        """Get PQC-specific attack vectors"""
        return [
            AttackVector(
                vector_id="pqc_side_channel",
                name="Side-Channel Attack on PQC Implementation",
                attack_type=AttackType.CRYPTOGRAPHIC,
                entry_points=["Timing analysis", "Power analysis", "Cache attacks"],
                prerequisites=["Physical or network access to timing information"],
                impact="Recovery of private keys, signature forgery",
                likelihood=0.3,
                detection_difficulty=0.8
            ),
            AttackVector(
                vector_id="pqc_weak_implementation",
                name="Weak PQC Implementation Exploitation",
                attack_type=AttackType.CRYPTOGRAPHIC,
                entry_points=["Weak randomness", "Key reuse", "Parameter manipulation"],
                prerequisites=["Access to multiple signatures/encryptions"],
                impact="Key recovery, signature forgery, message decryption",
                likelihood=0.4,
                detection_difficulty=0.6
            )
        ]

class OTELSecurityScanner(RedTeamScanner):
    """Scanner for OpenTelemetry security issues"""
    
    def __init__(self, target_path: Path):
        super().__init__("OTELSecurityScanner", target_path)
        
    async def scan(self) -> List[VulnerabilityReport]:
        """Scan OTEL implementation for security issues"""
        self.vulnerabilities = []
        
        otel_path = self.target_path / "src" / "dslmodel" / "otel"
        if not otel_path.exists():
            return self.vulnerabilities
        
        # Check for telemetry data leaks
        await self._check_telemetry_leaks(otel_path)
        
        # Check for insecure exporters
        await self._check_insecure_exporters(otel_path)
        
        # Check for excessive logging
        await self._check_excessive_logging(otel_path)
        
        return self.vulnerabilities
    
    async def _check_telemetry_leaks(self, otel_path: Path):
        """Check for sensitive data in telemetry"""
        sensitive_patterns = [
            r"password\s*[:=]\s*['\"][^'\"]+['\"]",
            r"secret\s*[:=]\s*['\"][^'\"]+['\"]",
            r"token\s*[:=]\s*['\"][^'\"]+['\"]",
            r"api_key\s*[:=]\s*['\"][^'\"]+['\"]",
        ]
        
        for py_file in otel_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                for pattern in sensitive_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.vulnerabilities.append(VulnerabilityReport(
                            vulnerability_id=f"otel_data_leak_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                            title="Sensitive Data in OTEL Telemetry",
                            description="Sensitive information may be exposed in telemetry data",
                            severity=SeverityLevel.HIGH,
                            category=VulnerabilityCategory.A09_LOGGING_MONITORING_FAILURES,
                            attack_type=AttackType.TELEMETRY_LEAK,
                            affected_components=[str(py_file)],
                            file_path=str(py_file),
                            remediation="Implement data sanitization before telemetry export"
                        ))
                        
            except Exception:
                continue
    
    async def _check_insecure_exporters(self, otel_path: Path):
        """Check for insecure telemetry exporters"""
        for py_file in otel_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Check for HTTP instead of HTTPS
                if re.search(r"http://.*exporter", content, re.IGNORECASE):
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=f"otel_insecure_transport_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                        title="Insecure OTEL Transport",
                        description="Telemetry data transmitted over HTTP instead of HTTPS",
                        severity=SeverityLevel.MEDIUM,
                        category=VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES,
                        attack_type=AttackType.DATA_EXFILTRATION,
                        affected_components=[str(py_file)],
                        file_path=str(py_file),
                        remediation="Use HTTPS for all telemetry exports"
                    ))
                    
            except Exception:
                continue
    
    async def _check_excessive_logging(self, otel_path: Path):
        """Check for excessive logging that may impact performance"""
        for py_file in otel_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                # Count logging statements
                log_count = sum(1 for line in lines if re.search(r"(logger\.|logging\.)", line))
                
                if log_count > len(lines) * 0.1:  # More than 10% of lines are logging
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=f"otel_excessive_logging_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                        title="Excessive Logging in OTEL",
                        description="High density of logging statements may impact performance",
                        severity=SeverityLevel.LOW,
                        category=VulnerabilityCategory.A09_LOGGING_MONITORING_FAILURES,
                        attack_type=AttackType.DENIAL_OF_SERVICE,
                        affected_components=[str(py_file)],
                        file_path=str(py_file),
                        remediation="Review logging levels and reduce non-essential logging"
                    ))
                    
            except Exception:
                continue
    
    def get_attack_vectors(self) -> List[AttackVector]:
        """Get OTEL-specific attack vectors"""
        return [
            AttackVector(
                vector_id="telemetry_poisoning",
                name="Telemetry Data Poisoning",
                attack_type=AttackType.TELEMETRY_LEAK,
                entry_points=["Malicious telemetry injection", "Man-in-the-middle attacks"],
                prerequisites=["Access to telemetry endpoints", "Insecure transport"],
                impact="False metrics, monitoring blind spots, data exfiltration",
                likelihood=0.4,
                detection_difficulty=0.7
            )
        ]

class SwarmCoordinationScanner(RedTeamScanner):
    """Scanner for SwarmAgent coordination security issues"""
    
    def __init__(self, target_path: Path):
        super().__init__("SwarmCoordinationScanner", target_path)
        
    async def scan(self) -> List[VulnerabilityReport]:
        """Scan swarm coordination for security issues"""
        self.vulnerabilities = []
        
        swarm_paths = [
            self.target_path / "src" / "dslmodel" / "commands" / "swarm.py",
            self.target_path / "src" / "dslmodel" / "swarm",
        ]
        
        for swarm_path in swarm_paths:
            if swarm_path.exists():
                await self._check_authorization(swarm_path)
                await self._check_command_injection(swarm_path)
                await self._check_agent_isolation(swarm_path)
        
        return self.vulnerabilities
    
    async def _check_authorization(self, swarm_path: Path):
        """Check for authorization issues in swarm coordination"""
        files_to_check = [swarm_path] if swarm_path.is_file() else list(swarm_path.rglob("*.py"))
        
        for py_file in files_to_check:
            try:
                content = py_file.read_text()
                
                # Check for missing authorization checks
                if ("agent" in content.lower() and "command" in content.lower() and 
                    not re.search(r"(auth|permission|access)", content, re.IGNORECASE)):
                    
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=f"swarm_no_auth_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                        title="Missing Authorization in Swarm Coordination",
                        description="Agent commands may execute without proper authorization checks",
                        severity=SeverityLevel.HIGH,
                        category=VulnerabilityCategory.A01_BROKEN_ACCESS_CONTROL,
                        attack_type=AttackType.AUTHORIZATION_BYPASS,
                        affected_components=[str(py_file)],
                        file_path=str(py_file),
                        remediation="Implement authorization checks for all agent commands"
                    ))
                    
            except Exception:
                continue
    
    async def _check_command_injection(self, swarm_path: Path):
        """Check for command injection in agent coordination"""
        files_to_check = [swarm_path] if swarm_path.is_file() else list(swarm_path.rglob("*.py"))
        
        for py_file in files_to_check:
            try:
                content = py_file.read_text()
                
                # Check for subprocess calls with user input
                if re.search(r"subprocess.*shell\s*=\s*True", content):
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=f"swarm_cmd_injection_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                        title="Command Injection Risk in Swarm",
                        description="Subprocess calls with shell=True may allow command injection",
                        severity=SeverityLevel.CRITICAL,
                        category=VulnerabilityCategory.A03_INJECTION,
                        attack_type=AttackType.CODE_INJECTION,
                        affected_components=[str(py_file)],
                        file_path=str(py_file),
                        remediation="Use subprocess with shell=False and argument lists"
                    ))
                    
            except Exception:
                continue
    
    async def _check_agent_isolation(self, swarm_path: Path):
        """Check for agent isolation issues"""
        files_to_check = [swarm_path] if swarm_path.is_file() else list(swarm_path.rglob("*.py"))
        
        for py_file in files_to_check:
            try:
                content = py_file.read_text()
                
                # Check for shared state without synchronization
                if (re.search(r"global\s+\w+", content) and 
                    not re.search(r"(lock|mutex|semaphore)", content, re.IGNORECASE)):
                    
                    self.vulnerabilities.append(VulnerabilityReport(
                        vulnerability_id=f"swarm_race_condition_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}",
                        title="Race Condition in Swarm State",
                        description="Shared global state without synchronization may cause race conditions",
                        severity=SeverityLevel.MEDIUM,
                        category=VulnerabilityCategory.A04_INSECURE_DESIGN,
                        attack_type=AttackType.DENIAL_OF_SERVICE,
                        affected_components=[str(py_file)],
                        file_path=str(py_file),
                        remediation="Implement proper synchronization for shared state"
                    ))
                    
            except Exception:
                continue
    
    def get_attack_vectors(self) -> List[AttackVector]:
        """Get swarm coordination attack vectors"""
        return [
            AttackVector(
                vector_id="swarm_takeover",
                name="Swarm Agent Takeover",
                attack_type=AttackType.AUTHORIZATION_BYPASS,
                entry_points=["Unauthenticated agent commands", "Agent impersonation"],
                prerequisites=["Missing authorization checks", "Network access to swarm"],
                impact="Full swarm control, malicious task execution",
                likelihood=0.6,
                detection_difficulty=0.5
            ),
            AttackVector(
                vector_id="swarm_coordination_attack",
                name="Coordination Protocol Attack",
                attack_type=AttackType.DENIAL_OF_SERVICE,
                entry_points=["Message flooding", "State corruption", "Resource exhaustion"],
                prerequisites=["Access to coordination channels"],
                impact="Swarm disruption, agent failure cascade",
                likelihood=0.5,
                detection_difficulty=0.4
            )
        ]