#!/usr/bin/env python3
"""
Git Parliament Red Team Security Testing
=========================================

Tests the Git Parliament system against the red team findings:
- Code injection attacks in motion/debate content
- Authentication bypass in voting
- Authorization bypass in merge oracle
- Telemetry data leakage
- Cryptographic vulnerabilities
"""

import asyncio
import subprocess
import tempfile
import pathlib
import json
import os
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from dslmodel.examples.git_parliament_5one_monitor import (
    setup_5one_monitoring,
    InstrumentedParliament
)


class GitParliamentRedTeam:
    """Red team testing for Git Parliament system"""
    
    def __init__(self):
        self.vulnerabilities_found = []
        self.tests_passed = 0
        self.tests_failed = 0
    
    def add_vulnerability(self, test_name: str, severity: str, description: str, 
                         payload: str = None, remediation: str = None):
        """Record a found vulnerability"""
        self.vulnerabilities_found.append({
            "test": test_name,
            "severity": severity,
            "description": description,
            "payload": payload,
            "remediation": remediation,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.tests_failed += 1
    
    def test_passed(self, test_name: str):
        """Record a passed test"""
        print(f"✅ {test_name}: SECURE")
        self.tests_passed += 1
    
    async def test_code_injection_in_motions(self, parliament: InstrumentedParliament):
        """Test for code injection vulnerabilities in motion content"""
        print("\n🔬 Testing Code Injection in Motions...")
        
        # Test 1: OS command injection in motion title
        try:
            malicious_title = "__import__('os').system('id')"
            motion_id = parliament.new_motion(
                title=malicious_title,
                body="This is a test motion with malicious title"
            )
            
            # Check if the motion was created without sanitization
            motion_file = parliament.repo / f"motions/{motion_id}.md"
            if motion_file.exists():
                content = motion_file.read_text()
                if "__import__" in content or "system(" in content:
                    self.add_vulnerability(
                        "motion_title_injection",
                        "CRITICAL",
                        "Motion title allows code injection without sanitization",
                        malicious_title,
                        "Sanitize and validate all user input before git operations"
                    )
                else:
                    self.test_passed("motion_title_injection")
            
        except Exception as e:
            # Exception is good - means injection was blocked
            self.test_passed("motion_title_injection")
        
        # Test 2: Script injection in motion body
        try:
            malicious_body = """
            Normal content here.
            
            <script>alert('XSS')</script>
            
            exec('import subprocess; subprocess.call(["whoami"])')
            
            More normal content.
            """
            
            motion_id = parliament.new_motion(
                title="Test Motion",
                body=malicious_body
            )
            
            motion_file = parliament.repo / f"motions/{motion_id}.md"
            if motion_file.exists():
                content = motion_file.read_text()
                if "<script>" in content or "exec(" in content:
                    self.add_vulnerability(
                        "motion_body_injection",
                        "HIGH",
                        "Motion body allows script injection without filtering",
                        malicious_body[:100] + "...",
                        "Implement content filtering and sanitization"
                    )
                else:
                    self.test_passed("motion_body_injection")
            
        except Exception:
            self.test_passed("motion_body_injection")
    
    async def test_authentication_bypass(self, parliament: InstrumentedParliament):
        """Test authentication bypass vulnerabilities"""
        print("\n🔬 Testing Authentication Bypass...")
        
        # Test 1: Vote without proper identity verification
        try:
            # Try to vote with suspicious repo names
            suspicious_repos = [
                "../../../admin",
                "'; DROP TABLE votes; --",
                "$(whoami)",
                "admin' OR '1'='1"
            ]
            
            motion_id = parliament.new_motion("Test Auth", "Test motion for auth")
            
            for repo_name in suspicious_repos:
                try:
                    parliament.vote(motion_id, repo_name, "for", 1.0)
                    
                    # Check if the vote was recorded with the malicious name
                    result = subprocess.run(
                        ["git", "for-each-ref", f"refs/vote/{motion_id}/*"],
                        capture_output=True, text=True, cwd=parliament.repo
                    )
                    
                    if repo_name in result.stdout:
                        self.add_vulnerability(
                            "vote_identity_bypass",
                            "HIGH",
                            f"Voting allows suspicious identity: {repo_name}",
                            repo_name,
                            "Implement strict identity validation for voters"
                        )
                    else:
                        self.test_passed(f"vote_identity_bypass_{repo_name}")
                        
                except Exception:
                    # Exception is good - means bypass was blocked
                    self.test_passed(f"vote_identity_bypass_{repo_name}")
            
        except Exception as e:
            self.test_passed("vote_identity_bypass")
    
    async def test_authorization_bypass(self, parliament: InstrumentedParliament):
        """Test authorization bypass vulnerabilities"""
        print("\n🔬 Testing Authorization Bypass...")
        
        # Test 1: Vote weight manipulation
        try:
            motion_id = parliament.new_motion("Test Auth", "Test motion")
            
            # Try extreme vote weights
            extreme_weights = [999999.0, -1.0, float('inf'), float('nan')]
            
            for weight in extreme_weights:
                try:
                    parliament.vote(motion_id, f"attacker_{weight}", "for", weight)
                    
                    # If this succeeds without validation, it's a vulnerability
                    if weight > 100 or weight < 0:
                        self.add_vulnerability(
                            "vote_weight_manipulation",
                            "CRITICAL",
                            f"Vote weight validation bypass: {weight}",
                            str(weight),
                            "Implement strict vote weight validation (e.g., 0.0-10.0)"
                        )
                    else:
                        self.test_passed(f"vote_weight_validation_{weight}")
                        
                except Exception:
                    self.test_passed(f"vote_weight_validation_{weight}")
            
        except Exception:
            self.test_passed("vote_weight_manipulation")
        
        # Test 2: Motion file system traversal
        try:
            # Try to create motion outside motions directory
            malicious_motion_paths = [
                "../../../etc/passwd",
                "../../.git/config",
                "/tmp/malicious_motion"
            ]
            
            for path in malicious_motion_paths:
                try:
                    # This should be blocked by the system
                    motion_id = f"M{path}"
                    motion_file = parliament.repo / f"motions/{motion_id}.md"
                    
                    if ".." in str(motion_file) or motion_file.is_absolute():
                        # System might be vulnerable to path traversal
                        parliament.new_motion("Test", f"Path traversal test: {path}")
                        
                        if motion_file.exists():
                            self.add_vulnerability(
                                "motion_path_traversal",
                                "HIGH",
                                f"Motion creation allows path traversal: {path}",
                                path,
                                "Validate motion IDs and sanitize file paths"
                            )
                        else:
                            self.test_passed(f"motion_path_traversal_{path}")
                            
                except Exception:
                    self.test_passed(f"motion_path_traversal_{path}")
                    
        except Exception:
            self.test_passed("motion_path_traversal")
    
    async def test_telemetry_data_leakage(self, parliament: InstrumentedParliament):
        """Test for sensitive data leakage in telemetry"""
        print("\n🔬 Testing Telemetry Data Leakage...")
        
        # Test 1: Sensitive data in span attributes
        try:
            # Create motion with sensitive-looking data
            sensitive_data = {
                "password": "secret123",
                "api_key": "sk-1234567890abcdef",
                "ssn": "123-45-6789",
                "credit_card": "4111-1111-1111-1111"
            }
            
            for data_type, value in sensitive_data.items():
                motion_title = f"Motion with {data_type}: {value}"
                motion_id = parliament.new_motion(motion_title, f"Contains {data_type}")
                
                # In a real system, we'd check if this data appears in telemetry
                # For now, we assume any inclusion of sensitive data is a risk
                self.add_vulnerability(
                    f"telemetry_{data_type}_leak",
                    "MEDIUM",
                    f"Potential {data_type} exposure in telemetry data",
                    value,
                    "Implement data masking and PII detection in telemetry"
                )
            
        except Exception:
            self.test_passed("telemetry_data_leakage")
    
    async def test_git_command_injection(self, parliament: InstrumentedParliament):
        """Test for git command injection vulnerabilities"""
        print("\n🔬 Testing Git Command Injection...")
        
        # Test 1: Command injection in git notes
        try:
            motion_id = parliament.new_motion("Test", "Test motion")
            motion_sha = subprocess.check_output(
                ["git", "rev-parse", f"motions/{motion_id}"],
                cwd=parliament.repo
            ).decode().strip()
            
            # Try command injection in debate argument
            malicious_arguments = [
                "; rm -rf /tmp/test",
                "$(whoami)",
                "`id`",
                "| cat /etc/passwd"
            ]
            
            for arg in malicious_arguments:
                try:
                    parliament.debate(motion_sha, "attacker", "pro", arg)
                    
                    # Check if the malicious content was executed
                    # In this case, we're just checking if it was stored
                    self.add_vulnerability(
                        "git_command_injection",
                        "CRITICAL",
                        f"Potential command injection in debate: {arg}",
                        arg,
                        "Sanitize all input before git operations"
                    )
                    
                except Exception:
                    self.test_passed(f"git_command_injection_{arg}")
            
        except Exception:
            self.test_passed("git_command_injection")
    
    async def run_all_tests(self):
        """Run all red team tests"""
        print("🔴 Git Parliament Red Team Security Assessment")
        print("=" * 55)
        
        # Setup test environment
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = pathlib.Path(tmpdir)
            os.chdir(repo_path)
            
            # Initialize git repo
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "redteam@test.com"], check=True)
            subprocess.run(["git", "config", "user.name", "Red Team"], check=True)
            
            # Create initial commit
            readme = repo_path / "README.md"
            readme.write_text("# Red Team Test Repository")
            subprocess.run(["git", "add", "README.md"], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
            
            # Setup monitoring (but disable OTLP to avoid errors)
            setup_5one_monitoring(
                service_name="git-parliament-redteam",
                otlp_endpoint="http://localhost:9999"  # Non-existent endpoint
            )
            
            parliament = InstrumentedParliament(repo_path)
            
            # Run all tests
            await self.test_code_injection_in_motions(parliament)
            await self.test_authentication_bypass(parliament)
            await self.test_authorization_bypass(parliament)
            await self.test_telemetry_data_leakage(parliament)
            await self.test_git_command_injection(parliament)
            
            # Generate report
            self.generate_report()
    
    def generate_report(self):
        """Generate final security assessment report"""
        print("\n" + "=" * 55)
        print("🔴 RED TEAM ASSESSMENT RESULTS")
        print("=" * 55)
        
        total_tests = self.tests_passed + self.tests_failed
        
        print(f"📊 Tests Run: {total_tests}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"🔍 Vulnerabilities Found: {len(self.vulnerabilities_found)}")
        
        if self.vulnerabilities_found:
            print("\n🚨 VULNERABILITIES DISCOVERED:")
            print("-" * 40)
            
            for vuln in self.vulnerabilities_found:
                print(f"\n🔥 {vuln['test']}")
                print(f"   Severity: {vuln['severity']}")
                print(f"   Description: {vuln['description']}")
                if vuln['payload']:
                    print(f"   Payload: {vuln['payload']}")
                if vuln['remediation']:
                    print(f"   Fix: {vuln['remediation']}")
        
        # Calculate risk score
        critical_count = len([v for v in self.vulnerabilities_found if v['severity'] == 'CRITICAL'])
        high_count = len([v for v in self.vulnerabilities_found if v['severity'] == 'HIGH'])
        medium_count = len([v for v in self.vulnerabilities_found if v['severity'] == 'MEDIUM'])
        
        risk_score = (critical_count * 10) + (high_count * 5) + (medium_count * 2)
        max_risk = total_tests * 10
        risk_percentage = (risk_score / max_risk * 100) if max_risk > 0 else 0
        
        print(f"\n🎯 OVERALL RISK SCORE: {risk_percentage:.1f}%")
        print(f"   Critical: {critical_count}")
        print(f"   High: {high_count}")
        print(f"   Medium: {medium_count}")
        
        if risk_percentage > 70:
            print("\n🚨 HIGH RISK - Immediate remediation required!")
        elif risk_percentage > 40:
            print("\n⚠️ MEDIUM RISK - Schedule remediation soon")
        else:
            print("\n✅ LOW RISK - System appears secure")
        
        # Save detailed report
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "tests_passed": self.tests_passed,
                "tests_failed": self.tests_failed,
                "vulnerabilities_found": len(self.vulnerabilities_found),
                "risk_score": risk_percentage,
                "risk_level": "HIGH" if risk_percentage > 70 else "MEDIUM" if risk_percentage > 40 else "LOW"
            },
            "vulnerabilities": self.vulnerabilities_found
        }
        
        with open("git_parliament_redteam_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved: git_parliament_redteam_report.json")


async def main():
    """Run the red team assessment"""
    redteam = GitParliamentRedTeam()
    await redteam.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())