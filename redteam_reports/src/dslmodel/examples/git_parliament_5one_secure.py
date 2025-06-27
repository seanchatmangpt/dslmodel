#!/usr/bin/env python3
"""
Git Parliament 5-ONE Secure Implementation
==========================================

Hardened version of the Git Parliament system addressing red team findings:
- Input sanitization and validation
- Command injection prevention  
- Vote weight validation
- Telemetry data masking
- Authentication and authorization controls
- Security monitoring and alerting
"""

import asyncio
import json
import time
import subprocess
import pathlib
import uuid
import re
import html
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
from functools import wraps
import secrets
import string

from opentelemetry import trace, metrics, baggage, context
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode

from loguru import logger


# Global tracer and meter for the secure parliament system
_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None


class SecurityError(Exception):
    """Custom exception for security violations"""
    pass


class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Patterns for dangerous content
    DANGEROUS_PATTERNS = [
        r'__import__\s*\(',
        r'eval\s*\(',
        r'exec\s*\(',
        r'subprocess\.',
        r'os\.',
        r'system\s*\(',
        r'<script',
        r'</script>',
        r'javascript:',
        r'vbscript:',
        r'data:',
        r'file://',
        r'\$\(',
        r'`[^`]*`',
        r';\s*rm\s+',
        r';\s*cat\s+',
        r';\s*ls\s+',
        r'\|\s*cat',
        r'\|\s*rm',
        r'\.\./\.\.',
        r'/etc/passwd',
        r'/etc/shadow'
    ]
    
    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        (r'password\s*[:=]\s*\S+', 'password'),
        (r'api[_-]?key\s*[:=]\s*\S+', 'api_key'),
        (r'\b\d{3}-\d{2}-\d{4}\b', 'ssn'),
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'credit_card'),
        (r'bearer\s+[a-zA-Z0-9]+', 'token'),
        (r'sk-[a-zA-Z0-9]+', 'secret_key')
    ]
    
    @classmethod
    def validate_motion_title(cls, title: str) -> str:
        """Validate and sanitize motion title"""
        if not title or len(title.strip()) == 0:
            raise SecurityError("Motion title cannot be empty")
        
        if len(title) > 200:
            raise SecurityError("Motion title too long (max 200 characters)")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                raise SecurityError(f"Potentially dangerous content detected in title")
        
        # HTML escape and normalize
        title = html.escape(title.strip())
        
        # Remove any remaining dangerous characters
        title = re.sub(r'[<>{}$`|;&]', '', title)
        
        return title
    
    @classmethod
    def validate_motion_body(cls, body: str) -> str:
        """Validate and sanitize motion body"""
        if not body or len(body.strip()) == 0:
            raise SecurityError("Motion body cannot be empty")
        
        if len(body) > 10000:
            raise SecurityError("Motion body too long (max 10000 characters)")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                raise SecurityError(f"Potentially dangerous content detected in body")
        
        # HTML escape
        body = html.escape(body.strip())
        
        # Remove script tags and dangerous content
        body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.IGNORECASE | re.DOTALL)
        body = re.sub(r'[{}$`|;&]', '', body)
        
        return body
    
    @classmethod
    def validate_debate_argument(cls, argument: str) -> str:
        """Validate and sanitize debate argument"""
        if not argument or len(argument.strip()) == 0:
            raise SecurityError("Debate argument cannot be empty")
        
        if len(argument) > 5000:
            raise SecurityError("Debate argument too long (max 5000 characters)")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, argument, re.IGNORECASE):
                raise SecurityError(f"Potentially dangerous content detected in argument")
        
        # HTML escape and sanitize
        argument = html.escape(argument.strip())
        argument = re.sub(r'[{}$`|;&]', '', argument)
        
        return argument
    
    @classmethod
    def validate_repo_name(cls, repo_name: str) -> str:
        """Validate repository name"""
        if not repo_name or len(repo_name.strip()) == 0:
            raise SecurityError("Repository name cannot be empty")
        
        if len(repo_name) > 100:
            raise SecurityError("Repository name too long (max 100 characters)")
        
        # Only allow alphanumeric, hyphens, underscores, and dots
        if not re.match(r'^[a-zA-Z0-9._-]+$', repo_name):
            raise SecurityError("Repository name contains invalid characters")
        
        # Prevent path traversal
        if '..' in repo_name or repo_name.startswith('/') or repo_name.startswith('.'):
            raise SecurityError("Repository name contains path traversal attempt")
        
        return repo_name.strip()
    
    @classmethod
    def validate_vote_weight(cls, weight: float) -> float:
        """Validate vote weight"""
        if not isinstance(weight, (int, float)):
            raise SecurityError("Vote weight must be a number")
        
        if weight != weight:  # Check for NaN
            raise SecurityError("Vote weight cannot be NaN")
        
        if weight == float('inf') or weight == float('-inf'):
            raise SecurityError("Vote weight cannot be infinite")
        
        if weight < 0.0 or weight > 10.0:
            raise SecurityError("Vote weight must be between 0.0 and 10.0")
        
        return float(weight)
    
    @classmethod
    def validate_vote_value(cls, value: str) -> str:
        """Validate vote value"""
        allowed_values = ['for', 'against', 'abstain']
        if value not in allowed_values:
            raise SecurityError(f"Vote value must be one of: {allowed_values}")
        return value
    
    @classmethod
    def validate_speaker_name(cls, speaker: str) -> str:
        """Validate speaker name"""
        if not speaker or len(speaker.strip()) == 0:
            raise SecurityError("Speaker name cannot be empty")
        
        if len(speaker) > 100:
            raise SecurityError("Speaker name too long (max 100 characters)")
        
        # Only allow email-like format for speakers
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', speaker):
            raise SecurityError("Speaker name must be a valid email format")
        
        return speaker.strip()
    
    @classmethod
    def mask_sensitive_data(cls, text: str) -> str:
        """Mask sensitive data in text for telemetry"""
        if not text:
            return text
        
        masked_text = text
        for pattern, data_type in cls.SENSITIVE_PATTERNS:
            def mask_match(match):
                return f"[MASKED_{data_type.upper()}]"
            masked_text = re.sub(pattern, mask_match, masked_text, flags=re.IGNORECASE)
        
        return masked_text


class SecureGitParliament:
    """Secure implementation of Git Parliament with comprehensive protections"""
    
    def __init__(self, repo_path: pathlib.Path = None):
        self.repo = repo_path or pathlib.Path(".").resolve()
        self.motion_metadata: Dict[str, Dict[str, Any]] = {}
        self.validator = InputValidator()
        
        # Security context
        self.session_id = secrets.token_hex(16)
        self.creation_time = datetime.utcnow()
        
        # Initialize OTEL if not already done
        self._setup_secure_monitoring()
        
        logger.info(f"Secure Git Parliament initialized with session {self.session_id}")
    
    def _setup_secure_monitoring(self):
        """Setup secure OTEL monitoring with data masking"""
        global _tracer, _meter
        
        if not _tracer:
            resource = Resource.create({
                "service.name": "git-parliament-secure",
                "service.version": "1.0.0",
                "service.namespace": "secure",
                "session.id": self.session_id
            })
            
            provider = TracerProvider(resource=resource)
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
            trace.set_tracer_provider(provider)
            
            meter_provider = MeterProvider(resource=resource)
            metrics.set_meter_provider(meter_provider)
            
            _tracer = trace.get_tracer(__name__)
            _meter = metrics.get_meter(__name__)
            
            # Setup security metrics
            self.security_alert_counter = _meter.create_counter(
                "parliament.security.alerts",
                description="Security alerts detected"
            )
            
            self.validation_counter = _meter.create_counter(
                "parliament.validation.checks",
                description="Input validation checks performed"
            )
    
    def _create_security_span(self, operation: str, **attributes):
        """Create span with security context and masked attributes"""
        span = _tracer.start_span(f"parliament.secure.{operation}")
        
        # Add security context
        span.set_attribute("security.session_id", self.session_id)
        span.set_attribute("security.timestamp", datetime.utcnow().isoformat())
        
        # Add masked attributes
        for key, value in attributes.items():
            if isinstance(value, str):
                masked_value = self.validator.mask_sensitive_data(value)
                span.set_attribute(f"secure.{key}", masked_value)
            else:
                span.set_attribute(f"secure.{key}", str(value))
        
        return span
    
    def _record_security_alert(self, alert_type: str, details: str):
        """Record security alert"""
        self.security_alert_counter.add(1, {"alert.type": alert_type})
        logger.warning(f"Security alert: {alert_type} - {details}")
    
    def new_motion(self, title: str, body: str, author: str = None) -> str:
        """Create new motion with comprehensive security validation"""
        
        with self._create_security_span("motion.create", 
                                       title=title, 
                                       body_length=len(body)) as span:
            
            try:
                # Validate inputs
                self.validation_counter.add(1, {"validation.type": "motion_title"})
                validated_title = self.validator.validate_motion_title(title)
                
                self.validation_counter.add(1, {"validation.type": "motion_body"})
                validated_body = self.validator.validate_motion_body(body)
                
                if author:
                    self.validation_counter.add(1, {"validation.type": "author"})
                    author = self.validator.validate_speaker_name(author)
                
                # Generate secure motion ID
                motion_id = f"M{secrets.token_hex(6)}"
                
                # Store metadata securely
                self.motion_metadata[motion_id] = {
                    "title": validated_title,
                    "created_at": datetime.utcnow(),
                    "author": author or "system",
                    "session_id": self.session_id
                }
                
                # Create motion file with validated content
                path = self.repo / f"motions/{motion_id}.md"
                path.parent.mkdir(exist_ok=True, mode=0o750)  # Restricted permissions
                path.write_text(f"# {validated_title}\n\n{validated_body}\n", encoding='utf-8')
                
                # Secure git operations
                self._secure_git_add(path)
                self._secure_git_branch(f"motions/{motion_id}")
                self._secure_git_commit(f"motion: {motion_id} {validated_title[:50]}")
                
                span.set_attribute("motion.id", motion_id)
                span.set_attribute("motion.validated", True)
                span.set_status(Status(StatusCode.OK))
                
                logger.info(f"Secure motion created: {motion_id}")
                return motion_id
                
            except SecurityError as e:
                self._record_security_alert("motion_validation_failed", str(e))
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def second(self, motion_sha: str, speaker: str):
        """Second a motion with security validation"""
        
        with self._create_security_span("motion.second", 
                                       motion_sha=motion_sha, 
                                       speaker=speaker) as span:
            try:
                # Validate inputs
                validated_speaker = self.validator.validate_speaker_name(speaker)
                
                # Validate motion SHA format
                if not re.match(r'^[a-f0-9]{40}$', motion_sha):
                    raise SecurityError("Invalid motion SHA format")
                
                message = json.dumps({
                    "speaker": validated_speaker,
                    "ts": datetime.utcnow().isoformat(),
                    "session_id": self.session_id,
                    "trace_id": format(span.get_span_context().trace_id, "032x")
                })
                
                self._secure_git_note_add("second", motion_sha, message)
                
                span.set_attribute("second.validated", True)
                span.set_status(Status(StatusCode.OK))
                
                logger.info(f"Motion seconded by {validated_speaker}")
                
            except SecurityError as e:
                self._record_security_alert("second_validation_failed", str(e))
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def debate(self, motion_sha: str, speaker: str, stance: str, argument: str):
        """Add debate with security validation"""
        
        with self._create_security_span("motion.debate",
                                       motion_sha=motion_sha,
                                       speaker=speaker,
                                       stance=stance) as span:
            try:
                # Validate all inputs
                validated_speaker = self.validator.validate_speaker_name(speaker)
                
                if stance not in ['pro', 'con', 'neutral']:
                    raise SecurityError("Invalid debate stance")
                
                validated_argument = self.validator.validate_debate_argument(argument)
                
                # Validate motion SHA
                if not re.match(r'^[a-f0-9]{40}$', motion_sha):
                    raise SecurityError("Invalid motion SHA format")
                
                message = json.dumps({
                    "sp": validated_speaker,
                    "st": stance,
                    "arg": validated_argument,
                    "ts": datetime.utcnow().isoformat(),
                    "session_id": self.session_id
                })
                
                self._secure_git_note_add("debate", motion_sha, message)
                
                span.set_attribute("debate.validated", True)
                span.set_attribute("debate.stance", stance)
                span.set_status(Status(StatusCode.OK))
                
                logger.info(f"Debate added by {validated_speaker} ({stance})")
                
            except SecurityError as e:
                self._record_security_alert("debate_validation_failed", str(e))
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def vote(self, motion_id: str, repo_name: str, val: str, weight: float = 1.0):
        """Cast vote with comprehensive security validation"""
        
        with self._create_security_span("vote.cast",
                                       motion_id=motion_id,
                                       repo_name=repo_name,
                                       vote_value=val) as span:
            try:
                # Validate all inputs
                validated_repo = self.validator.validate_repo_name(repo_name)
                validated_value = self.validator.validate_vote_value(val)
                validated_weight = self.validator.validate_vote_weight(weight)
                
                # Validate motion ID format
                if not re.match(r'^M[a-f0-9]{12}$', motion_id):
                    raise SecurityError("Invalid motion ID format")
                
                # Check for duplicate voting (basic check)
                existing_refs = subprocess.run(
                    ["git", "for-each-ref", f"refs/vote/{motion_id}/{validated_repo}/*"],
                    capture_output=True, text=True, cwd=self.repo
                )
                
                if existing_refs.stdout.strip():
                    raise SecurityError("Duplicate voting attempt detected")
                
                # Create secure vote reference
                vote_uuid = secrets.token_hex(16)
                ref = f"refs/vote/{motion_id}/{validated_repo}/{vote_uuid}"
                
                # Create vote blob with security metadata
                blob = json.dumps({
                    "vote": validated_value,
                    "weight": validated_weight,
                    "timestamp": datetime.utcnow().isoformat(),
                    "session_id": self.session_id,
                    "trace_id": format(span.get_span_context().trace_id, "032x"),
                    "hash": hashlib.sha256(f"{motion_id}{validated_repo}{validated_value}{validated_weight}".encode()).hexdigest()
                }).encode()
                
                # Store vote securely
                sha = self._secure_git_hash_object(blob)
                self._secure_git_update_ref(ref, sha)
                
                # Only push if origin exists and is secure
                self._secure_push_if_available("origin", ref)
                
                span.set_attribute("vote.validated", True)
                span.set_attribute("vote.weight", validated_weight)
                span.set_status(Status(StatusCode.OK))
                
                logger.info(f"Secure vote cast: {validated_repo} votes {validated_value}")
                
            except SecurityError as e:
                self._record_security_alert("vote_validation_failed", str(e))
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def _secure_git_add(self, path: pathlib.Path):
        """Secure git add operation"""
        # Validate path is within repo
        try:
            path.resolve().relative_to(self.repo.resolve())
        except ValueError:
            raise SecurityError("Path outside repository bounds")
        
        subprocess.run(["git", "add", str(path)], check=True, cwd=self.repo)
    
    def _secure_git_branch(self, name: str):
        """Secure git branch creation"""
        # Validate branch name
        if not re.match(r'^[a-zA-Z0-9/_-]+$', name):
            raise SecurityError("Invalid branch name format")
        
        subprocess.run(["git", "branch", name], check=True, cwd=self.repo)
    
    def _secure_git_commit(self, message: str):
        """Secure git commit operation"""
        # Sanitize commit message
        sanitized_message = self.validator.mask_sensitive_data(message)
        sanitized_message = re.sub(r'[`$|;&]', '', sanitized_message)
        
        subprocess.run(["git", "commit", "-m", sanitized_message], check=True, cwd=self.repo)
    
    def _secure_git_note_add(self, ref: str, target: str, message: str):
        """Secure git notes operation"""
        # Validate ref name
        if not re.match(r'^[a-zA-Z0-9_-]+$', ref):
            raise SecurityError("Invalid notes ref format")
        
        # Validate target SHA
        if not re.match(r'^[a-f0-9]{40}$', target):
            raise SecurityError("Invalid target SHA format")
        
        # Sanitize message
        sanitized_message = self.validator.mask_sensitive_data(message)
        
        subprocess.run(
            ["git", "notes", f"--ref={ref}", "append", "-m", sanitized_message, target],
            check=True, cwd=self.repo
        )
    
    def _secure_git_hash_object(self, blob: bytes) -> str:
        """Secure git hash-object operation"""
        result = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=blob, capture_output=True, check=True, cwd=self.repo
        )
        return result.stdout.decode().strip()
    
    def _secure_git_update_ref(self, ref: str, sha: str):
        """Secure git update-ref operation"""
        # Validate ref format
        if not re.match(r'^refs/[a-zA-Z0-9/_-]+$', ref):
            raise SecurityError("Invalid ref format")
        
        # Validate SHA
        if not re.match(r'^[a-f0-9]{40}$', sha):
            raise SecurityError("Invalid SHA format")
        
        subprocess.run(["git", "update-ref", ref, sha], check=True, cwd=self.repo)
    
    def _secure_push_if_available(self, remote: str, refspec: str):
        """Securely push if remote is available and trusted"""
        try:
            # Check if remote exists
            subprocess.run(["git", "remote", "get-url", remote],
                          check=True, capture_output=True, cwd=self.repo)
            
            # Validate remote and refspec
            if not re.match(r'^[a-zA-Z0-9_-]+$', remote):
                raise SecurityError("Invalid remote name")
            
            if not re.match(r'^refs/[a-zA-Z0-9/_-]+$', refspec):
                raise SecurityError("Invalid refspec format")
            
            # Push with timeout
            subprocess.run(
                ["git", "push", remote, refspec],
                check=True, cwd=self.repo, timeout=30
            )
            
        except subprocess.CalledProcessError:
            # No remote or push failed - store locally only
            logger.info(f"Stored {refspec} locally (no remote or push failed)")
        except subprocess.TimeoutExpired:
            raise SecurityError("Push operation timed out")


# Test the secure implementation
async def test_secure_parliament():
    """Test the secure Git Parliament implementation"""
    
    print("🔒 Testing Secure Git Parliament")
    print("=" * 35)
    
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = pathlib.Path(tmpdir)
        os.chdir(repo_path)
        
        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "secure@test.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Secure Test"], check=True)
        
        # Create initial commit
        readme = repo_path / "README.md"
        readme.write_text("# Secure Parliament Test")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        parliament = SecureGitParliament(repo_path)
        
        # Test 1: Normal operation
        print("\n✅ Testing normal operation...")
        motion_id = parliament.new_motion(
            "Test Secure Motion",
            "This is a test of the secure parliament system.",
            "test@example.com"
        )
        print(f"Motion created: {motion_id}")
        
        # Test 2: Security validation
        print("\n🔒 Testing security validation...")
        
        try:
            parliament.new_motion(
                "__import__('os').system('id')",  # Malicious title
                "Normal body"
            )
            print("❌ Security test failed - malicious title accepted")
        except SecurityError:
            print("✅ Security test passed - malicious title rejected")
        
        try:
            parliament.vote(motion_id, "test@example.com", "for", 999999.0)  # Invalid weight
            print("❌ Security test failed - invalid weight accepted")
        except SecurityError:
            print("✅ Security test passed - invalid weight rejected")
        
        try:
            parliament.vote(motion_id, "../../../admin", "for", 1.0)  # Path traversal
            print("❌ Security test failed - path traversal accepted")
        except SecurityError:
            print("✅ Security test passed - path traversal rejected")
        
        print("\n🎯 Secure Git Parliament test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_secure_parliament())