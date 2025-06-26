"""
DSLModel Automated Red Team CLI Commands
Comprehensive security testing and vulnerability assessment
"""

import typer
import asyncio
from pathlib import Path
from typing import Optional, List
import json
from datetime import datetime
import uuid

from ..redteam import (
    RedTeamEngine, SecurityReportGenerator, AdversarialTestGenerator,
    PenetrationTester, CryptoAttacker, TelemetryProber
)
from ..redteam.scanners import (
    CodeVulnerabilityScanner, DependencyScanner, PQCCryptoScanner,
    OTELSecurityScanner, SwarmCoordinationScanner
)

app = typer.Typer(help="Automated Red Team security testing")

@app.command("scan")
def run_security_scan(
    target_path: Optional[Path] = typer.Option(
        None,
        "--target", "-t",
        help="Target path to scan (defaults to current directory)"
    ),
    scanners: Optional[str] = typer.Option(
        "all",
        "--scanners", "-s",
        help="Comma-separated list of scanners: code,deps,pqc,otel,swarm,all"
    ),
    output_dir: Optional[Path] = typer.Option(
        Path("redteam_reports"),
        "--output", "-o",
        help="Output directory for reports"
    ),
    report_format: str = typer.Option(
        "json",
        "--format", "-f",
        help="Report format: json, markdown, both"
    )
):
    """Run comprehensive security scan on DSLModel implementation"""
    
    if target_path is None:
        target_path = Path.cwd()
    
    typer.echo("🔴 DSLModel Automated Red Team Security Scan")
    typer.echo("=" * 60)
    typer.echo(f"Target: {target_path}")
    typer.echo(f"Scanners: {scanners}")
    typer.echo("")
    
    async def run_scan():
        # Initialize red team engine
        session_id = f"redteam_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        engine = RedTeamEngine(
            session_id=session_id,
            target_path=target_path
        )
        
        # Register scanners based on selection
        scanner_list = scanners.lower().split(",") if scanners != "all" else ["code", "deps", "pqc", "otel", "swarm"]
        
        if "code" in scanner_list or "all" in scanner_list:
            typer.echo("🔍 Registering Code Vulnerability Scanner...")
            engine.register_scanner(CodeVulnerabilityScanner(target_path))
        
        if "deps" in scanner_list or "all" in scanner_list:
            typer.echo("🔍 Registering Dependency Scanner...")
            engine.register_scanner(DependencyScanner(target_path))
        
        if "pqc" in scanner_list or "all" in scanner_list:
            typer.echo("🔍 Registering PQC Crypto Scanner...")
            engine.register_scanner(PQCCryptoScanner(target_path))
        
        if "otel" in scanner_list or "all" in scanner_list:
            typer.echo("🔍 Registering OTEL Security Scanner...")
            engine.register_scanner(OTELSecurityScanner(target_path))
        
        if "swarm" in scanner_list or "all" in scanner_list:
            typer.echo("🔍 Registering Swarm Coordination Scanner...")
            engine.register_scanner(SwarmCoordinationScanner(target_path))
        
        typer.echo(f"\n🚀 Starting comprehensive scan with {len(engine.active_scanners)} scanners...")
        
        # Run the scan
        results = await engine.run_comprehensive_scan()
        
        # Generate reports
        typer.echo("\n📊 Generating security reports...")
        report_gen = SecurityReportGenerator()
        comprehensive_report = report_gen.generate_comprehensive_report(engine)
        
        # Save reports
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if report_format in ["json", "both"]:
            json_path = output_dir / f"redteam_report_{session_id}.json"
            report_gen.save_report(comprehensive_report, json_path, "json")
            typer.echo(f"📄 JSON report saved: {json_path}")
        
        if report_format in ["markdown", "both"]:
            md_path = output_dir / f"redteam_report_{session_id}.md"
            report_gen.save_report(comprehensive_report, md_path, "markdown")
            typer.echo(f"📄 Markdown report saved: {md_path}")
        
        # Display summary
        typer.echo("\n" + "=" * 60)
        typer.echo("🎯 RED TEAM SCAN SUMMARY")
        typer.echo("=" * 60)
        
        risk_assessment = comprehensive_report["risk_assessment"]
        
        # Calculate risk level from score
        score = risk_assessment['overall_risk_score']
        if score >= 8.0:
            risk_level = "CRITICAL"
        elif score >= 6.0:
            risk_level = "HIGH"
        elif score >= 4.0:
            risk_level = "MEDIUM"
        elif score >= 2.0:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        typer.echo(f"Overall Risk Level: {risk_level}")
        typer.echo(f"Risk Score: {score:.1f}/10")
        typer.echo(f"Total Vulnerabilities: {engine.total_vulnerabilities}")
        typer.echo(f"  🔴 Critical: {risk_assessment['critical_count']}")
        typer.echo(f"  🟠 High: {risk_assessment['high_count']}")
        typer.echo(f"  🟡 Medium: {risk_assessment['medium_count']}")
        typer.echo(f"  🔵 Low: {risk_assessment['low_count']}")
        typer.echo(f"  ⚪ Info: {risk_assessment['info_count']}")
        
        if engine.all_attack_vectors:
            typer.echo(f"\nAttack Vectors Identified: {len(engine.all_attack_vectors)}")
            for av in engine.all_attack_vectors[:3]:  # Show top 3
                typer.echo(f"  • {av.name} (likelihood: {av.likelihood:.1f})")
        
        # Show critical findings
        critical_findings = engine.get_critical_findings()
        if critical_findings:
            typer.echo(f"\n🚨 CRITICAL FINDINGS ({len(critical_findings)}):")
            for vuln in critical_findings[:5]:  # Show top 5
                typer.echo(f"  • {vuln.title}")
                if vuln.file_path:
                    typer.echo(f"    File: {vuln.file_path}:{vuln.line_number or '?'}")
        
        return comprehensive_report
    
    # Run the async scan
    report = asyncio.run(run_scan())
    return report

@app.command("adversarial")
def run_adversarial_tests(
    target_path: Optional[Path] = typer.Option(
        None,
        "--target", "-t", 
        help="Target path (defaults to current directory)"
    ),
    test_types: str = typer.Option(
        "all",
        "--types",
        help="Test types: injection,crypto,telemetry,auth,all"
    ),
    save_tests: bool = typer.Option(
        True,
        "--save",
        help="Save generated test cases"
    )
):
    """Generate and run adversarial security tests"""
    
    if target_path is None:
        target_path = Path.cwd()
    
    typer.echo("⚔️  DSLModel Adversarial Security Testing")
    typer.echo("=" * 60)
    
    # Generate adversarial tests
    test_gen = AdversarialTestGenerator()
    
    if test_types == "all":
        all_tests = test_gen.generate_all_tests()
    else:
        all_tests = []
        type_list = test_types.split(",")
        
        if "injection" in type_list:
            all_tests.extend(test_gen.generate_injection_tests())
        if "crypto" in type_list:
            all_tests.extend(test_gen.generate_crypto_tests())
        if "telemetry" in type_list:
            all_tests.extend(test_gen.generate_telemetry_tests())
        if "auth" in type_list:
            all_tests.extend(test_gen.generate_authorization_tests())
    
    typer.echo(f"Generated {len(all_tests)} adversarial test cases")
    
    # Display test summary
    by_attack_type = {}
    for test in all_tests:
        attack_type = test.attack_type.value
        by_attack_type[attack_type] = by_attack_type.get(attack_type, 0) + 1
    
    typer.echo("\nTest Distribution:")
    for attack_type, count in by_attack_type.items():
        typer.echo(f"  {attack_type}: {count} tests")
    
    # Save tests if requested
    if save_tests:
        test_file = target_path / "adversarial_tests.json"
        with open(test_file, 'w') as f:
            json.dump([test.dict() for test in all_tests], f, indent=2, default=str)
        typer.echo(f"\n📄 Tests saved: {test_file}")
    
    # Show sample tests
    typer.echo(f"\n🔬 Sample Adversarial Tests:")
    for i, test in enumerate(all_tests[:3]):
        typer.echo(f"\n{i+1}. {test.name}")
        typer.echo(f"   Type: {test.attack_type.value}")
        typer.echo(f"   Severity: {test.severity.value}")
        typer.echo(f"   Payload: {test.test_payload[:50]}..." if test.test_payload else "   Payload: N/A")
        typer.echo(f"   Expected: {test.expected_outcome}")

@app.command("pentest")
def run_penetration_test(
    target_path: Optional[Path] = typer.Option(
        None,
        "--target", "-t",
        help="Target path (defaults to current directory)"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for results"
    )
):
    """Run automated penetration testing"""
    
    if target_path is None:
        target_path = Path.cwd()
    
    if output_file is None:
        output_file = Path(f"pentest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    typer.echo("🎯 DSLModel Automated Penetration Testing")
    typer.echo("=" * 60)
    
    async def run_pentest():
        pentester = PenetrationTester(target_path)
        typer.echo("🔍 Running penetration tests...")
        
        results = await pentester.run_penetration_tests()
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Display summary
        typer.echo(f"\n📊 Penetration Test Results: {len(results)} findings")
        
        by_severity = {}
        for result in results:
            severity = result.get("severity", "UNKNOWN")
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        for severity, count in by_severity.items():
            typer.echo(f"  {severity}: {count}")
        
        # Show critical findings
        critical = [r for r in results if r.get("severity") == "CRITICAL"]
        if critical:
            typer.echo(f"\n🚨 Critical Findings ({len(critical)}):")
            for finding in critical:
                typer.echo(f"  • {finding['finding']}")
                typer.echo(f"    File: {finding.get('file', 'N/A')}")
        
        typer.echo(f"\n📄 Full results saved: {output_file}")
        return results
    
    return asyncio.run(run_pentest())

@app.command("crypto-attack")
def run_crypto_attacks(
    attack_types: str = typer.Option(
        "all",
        "--types",
        help="Attack types: timing,weak-random,hash-collision,all"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for attack results"
    )
):
    """Simulate cryptographic attacks"""
    
    if output_file is None:
        output_file = Path(f"crypto_attack_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    typer.echo("🔐 DSLModel Cryptographic Attack Simulation")
    typer.echo("=" * 60)
    
    async def run_crypto_attacks():
        attacker = CryptoAttacker()
        results = []
        
        attack_list = attack_types.split(",") if attack_types != "all" else ["timing", "weak-random", "hash-collision"]
        
        if "timing" in attack_list or "all" in attack_list:
            typer.echo("⏱️  Running timing attack simulation...")
            timing_result = await attacker.simulate_timing_attack("password_verification")
            results.append(timing_result)
            
            if timing_result["vulnerable"]:
                typer.echo("  🚨 VULNERABLE to timing attacks!")
            else:
                typer.echo("  ✅ Timing appears constant")
        
        if "weak-random" in attack_list or "all" in attack_list:
            typer.echo("🎲 Running weak randomness attack...")
            random_result = await attacker.simulate_weak_random_attack()
            results.append(random_result)
            
            if random_result["predictable"]:
                typer.echo("  🚨 VULNERABLE to prediction attacks!")
            else:
                typer.echo("  ✅ Random sequence appears unpredictable")
        
        if "hash-collision" in attack_list or "all" in attack_list:
            typer.echo("🔨 Running hash collision attack...")
            hash_result = await attacker.simulate_hash_collision_attack()
            results.append(hash_result)
            
            if hash_result["md5_vulnerable"]:
                typer.echo("  🚨 MD5 is vulnerable to collisions!")
            if not hash_result["sha256_vulnerable"]:
                typer.echo("  ✅ SHA-256 appears secure")
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        typer.echo(f"\n📄 Attack results saved: {output_file}")
        return results
    
    return asyncio.run(run_crypto_attacks())

@app.command("probe-telemetry")
def probe_telemetry_security(
    target_path: Optional[Path] = typer.Option(
        None,
        "--target", "-t",
        help="Target path (defaults to current directory)"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for probe results"
    )
):
    """Probe telemetry systems for security issues"""
    
    if target_path is None:
        target_path = Path.cwd()
    
    if output_file is None:
        output_file = Path(f"telemetry_probe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    typer.echo("📡 DSLModel Telemetry Security Probe")
    typer.echo("=" * 60)
    
    async def run_probe():
        prober = TelemetryProber(target_path)
        typer.echo("🔍 Probing telemetry systems...")
        
        results = await prober.probe_telemetry_leaks()
        
        # Display summary
        typer.echo(f"\n📊 Telemetry Probe Results: {len(results)} issues found")
        
        by_type = {}
        for result in results:
            probe_type = result.get("probe_type", "unknown")
            by_type[probe_type] = by_type.get(probe_type, 0) + 1
        
        for probe_type, count in by_type.items():
            typer.echo(f"  {probe_type}: {count}")
        
        # Show high severity issues
        high_severity = [r for r in results if r.get("severity") == "HIGH"]
        if high_severity:
            typer.echo(f"\n🚨 High Severity Issues ({len(high_severity)}):")
            for issue in high_severity:
                typer.echo(f"  • {issue['issue']}")
                typer.echo(f"    File: {issue.get('file', 'N/A')}")
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        typer.echo(f"\n📄 Probe results saved: {output_file}")
        return results
    
    return asyncio.run(run_probe())

@app.command("full-assessment")
def run_full_assessment(
    target_path: Optional[Path] = typer.Option(
        None,
        "--target", "-t",
        help="Target path (defaults to current directory)"
    ),
    output_dir: Optional[Path] = typer.Option(
        Path("redteam_assessment"),
        "--output", "-o", 
        help="Output directory for all reports"
    ),
    include_attacks: bool = typer.Option(
        True,
        "--attacks",
        help="Include attack simulations"
    )
):
    """Run complete security assessment with all tools"""
    
    if target_path is None:
        target_path = Path.cwd()
    
    typer.echo("🔴 DSLModel Complete Security Assessment")
    typer.echo("=" * 60)
    typer.echo(f"Target: {target_path}")
    typer.echo(f"Output: {output_dir}")
    typer.echo("")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    assessment_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Run comprehensive scan
    typer.echo("1️⃣ Running comprehensive security scan...")
    scan_result = asyncio.run(_run_full_scan(target_path, output_dir, assessment_id))
    
    # 2. Generate adversarial tests
    typer.echo("\n2️⃣ Generating adversarial tests...")
    test_gen = AdversarialTestGenerator()
    tests = test_gen.generate_all_tests()
    
    test_file = output_dir / f"adversarial_tests_{assessment_id}.json"
    with open(test_file, 'w') as f:
        json.dump([test.dict() for test in tests], f, indent=2, default=str)
    typer.echo(f"   Generated {len(tests)} test cases")
    
    # 3. Run penetration testing
    typer.echo("\n3️⃣ Running penetration tests...")
    pentest_file = output_dir / f"pentest_results_{assessment_id}.json"
    pentest_results = asyncio.run(_run_pentest(target_path, pentest_file))
    
    # 4. Attack simulations (if enabled)
    if include_attacks:
        typer.echo("\n4️⃣ Running attack simulations...")
        
        # Crypto attacks
        crypto_file = output_dir / f"crypto_attacks_{assessment_id}.json"
        crypto_results = asyncio.run(_run_crypto_attacks(crypto_file))
        
        # Telemetry probe
        telemetry_file = output_dir / f"telemetry_probe_{assessment_id}.json"
        telemetry_results = asyncio.run(_run_telemetry_probe(target_path, telemetry_file))
    
    # 5. Generate final assessment report
    typer.echo("\n5️⃣ Generating final assessment report...")
    
    final_report = {
        "assessment_metadata": {
            "id": assessment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "target_path": str(target_path),
            "tools_used": ["scanner", "adversarial", "pentest"] + (["crypto_attacks", "telemetry_probe"] if include_attacks else [])
        },
        "scan_results": scan_result,
        "adversarial_tests_count": len(tests),
        "pentest_findings": len(pentest_results) if pentest_results else 0
    }
    
    if include_attacks:
        final_report["attack_simulations"] = {
            "crypto_vulnerabilities": len([r for r in crypto_results if r.get("vulnerable", False)]),
            "telemetry_issues": len(telemetry_results) if telemetry_results else 0
        }
    
    final_report_file = output_dir / f"final_assessment_{assessment_id}.json"
    with open(final_report_file, 'w') as f:
        json.dump(final_report, f, indent=2, default=str)
    
    # Display final summary
    typer.echo("\n" + "=" * 60)
    typer.echo("🎯 COMPLETE SECURITY ASSESSMENT SUMMARY")
    typer.echo("=" * 60)
    
    if scan_result and "risk_assessment" in scan_result:
        risk = scan_result["risk_assessment"]
        typer.echo(f"Overall Risk Score: {risk['overall_risk_score']:.1f}/10")
        typer.echo(f"Critical Vulnerabilities: {risk['critical_count']}")
        typer.echo(f"High Severity Issues: {risk['high_count']}")
    
    typer.echo(f"Adversarial Tests Generated: {len(tests)}")
    typer.echo(f"Penetration Test Findings: {len(pentest_results) if pentest_results else 0}")
    
    if include_attacks:
        vulnerable_attacks = len([r for r in crypto_results if r.get("vulnerable", False)])
        typer.echo(f"Vulnerable to Crypto Attacks: {vulnerable_attacks}")
        typer.echo(f"Telemetry Security Issues: {len(telemetry_results) if telemetry_results else 0}")
    
    typer.echo(f"\n📁 All reports saved in: {output_dir}")
    typer.echo(f"📄 Final assessment: {final_report_file}")
    
    return final_report

async def _run_full_scan(target_path: Path, output_dir: Path, assessment_id: str):
    """Helper to run full security scan"""
    from ..redteam import RedTeamEngine, SecurityReportGenerator
    from ..redteam.scanners import (
        CodeVulnerabilityScanner, DependencyScanner, PQCCryptoScanner,
        OTELSecurityScanner, SwarmCoordinationScanner
    )
    
    session_id = f"assessment_{assessment_id}"
    engine = RedTeamEngine(session_id=session_id, target_path=target_path)
    
    # Register all scanners
    engine.register_scanner(CodeVulnerabilityScanner(target_path))
    engine.register_scanner(DependencyScanner(target_path))
    engine.register_scanner(PQCCryptoScanner(target_path))
    engine.register_scanner(OTELSecurityScanner(target_path))
    engine.register_scanner(SwarmCoordinationScanner(target_path))
    
    # Run scan
    results = await engine.run_comprehensive_scan()
    
    # Generate report
    report_gen = SecurityReportGenerator()
    comprehensive_report = report_gen.generate_comprehensive_report(engine)
    
    # Save
    report_file = output_dir / f"security_scan_{assessment_id}.json"
    report_gen.save_report(comprehensive_report, report_file, "json")
    
    return comprehensive_report

async def _run_pentest(target_path: Path, output_file: Path):
    """Helper to run penetration test"""
    pentester = PenetrationTester(target_path)
    results = await pentester.run_penetration_tests()
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results

async def _run_crypto_attacks(output_file: Path):
    """Helper to run crypto attacks"""
    attacker = CryptoAttacker()
    results = []
    
    results.append(await attacker.simulate_timing_attack("test_function"))
    results.append(await attacker.simulate_weak_random_attack())
    results.append(await attacker.simulate_hash_collision_attack())
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results

async def _run_telemetry_probe(target_path: Path, output_file: Path):
    """Helper to run telemetry probe"""
    prober = TelemetryProber(target_path)
    results = await prober.probe_telemetry_leaks()
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results

if __name__ == "__main__":
    app()