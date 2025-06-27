#!/usr/bin/env python3
"""
Self-Evolving Semantics for Swarm SH 5-ONE
==========================================

Meta-agents that propose changes to their own semantic conventions.
Automatic CI approves low-risk grammar patches.
"""

import json
import yaml
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import difflib
import hashlib

from loguru import logger
from ..core.weaver_engine import WeaverEngine
from ..validation.weaver_otel_validator import WeaverOTELValidator


class EvolutionRisk(Enum):
    """Risk levels for semantic evolution"""
    LOW = "low"        # Grammar fixes, documentation
    MEDIUM = "medium"  # New optional attributes
    HIGH = "high"      # Breaking changes, required fields
    CRITICAL = "critical"  # Core convention changes


@dataclass
class SemanticPatch:
    """Proposed change to semantic convention"""
    id: str
    convention_name: str
    patch_type: str  # add_attribute, modify_rule, fix_grammar
    description: str
    diff: str
    risk_level: EvolutionRisk
    confidence: float
    proposer_agent: str
    validation_results: Dict[str, Any] = field(default_factory=dict)
    approved: bool = False
    applied: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvolutionMetrics:
    """Metrics from semantic evolution"""
    total_proposals: int = 0
    approved_patches: int = 0
    rejected_patches: int = 0
    auto_approved: int = 0
    validation_improvements: float = 0.0
    grammar_fixes: int = 0
    breaking_changes: int = 0


class MetaAgent:
    """Agent that can modify its own semantic conventions"""
    
    def __init__(self, agent_id: str, convention_path: Path):
        self.agent_id = agent_id
        self.convention_path = convention_path
        self.weaver = WeaverEngine()
        self.validator = WeaverOTELValidator()
        self.evolution_history = []
        
    async def analyze_convention(self) -> List[SemanticPatch]:
        """Analyze current convention and propose improvements"""
        patches = []
        
        # Load current convention
        with open(self.convention_path) as f:
            convention = yaml.safe_load(f)
        
        # 1. Grammar and consistency checks
        grammar_patches = self._check_grammar(convention)
        patches.extend(grammar_patches)
        
        # 2. Analyze telemetry patterns for missing attributes
        pattern_patches = await self._analyze_telemetry_patterns(convention)
        patches.extend(pattern_patches)
        
        # 3. Check for optimization opportunities
        optimization_patches = self._check_optimizations(convention)
        patches.extend(optimization_patches)
        
        return patches
    
    def _check_grammar(self, convention: Dict) -> List[SemanticPatch]:
        """Check for grammar and consistency issues"""
        patches = []
        
        # Check attribute descriptions
        if 'groups' in convention:
            for group in convention['groups']:
                if 'attributes' in group:
                    for attr in group['attributes']:
                        if 'brief' in attr:
                            brief = attr['brief']
                            # Check capitalization
                            if brief and not brief[0].isupper():
                                patch = SemanticPatch(
                                    id=f"grammar-{attr.get('id', 'unknown')}-caps",
                                    convention_name=self.convention_path.stem,
                                    patch_type="fix_grammar",
                                    description=f"Capitalize attribute brief: {attr.get('id')}",
                                    diff=f"- brief: {brief}\n+ brief: {brief[0].upper() + brief[1:]}",
                                    risk_level=EvolutionRisk.LOW,
                                    confidence=0.95,
                                    proposer_agent=self.agent_id
                                )
                                patches.append(patch)
        
        return patches
    
    async def _analyze_telemetry_patterns(self, convention: Dict) -> List[SemanticPatch]:
        """Analyze telemetry to find missing attributes"""
        patches = []
        
        # Simulate telemetry analysis
        # In production, would query actual OTEL data
        common_attributes = {
            "trace.id": 0.98,
            "span.id": 0.97,
            "duration_ms": 0.95,
            "error.type": 0.15,
            "retry.count": 0.12
        }
        
        # Check if common attributes are missing
        existing_attrs = set()
        if 'groups' in convention:
            for group in convention['groups']:
                if 'attributes' in group:
                    for attr in group['attributes']:
                        existing_attrs.add(attr.get('id'))
        
        for attr_name, frequency in common_attributes.items():
            if attr_name not in existing_attrs and frequency > 0.9:
                patch = SemanticPatch(
                    id=f"add-attr-{attr_name.replace('.', '-')}",
                    convention_name=self.convention_path.stem,
                    patch_type="add_attribute",
                    description=f"Add commonly used attribute: {attr_name}",
                    diff=f"+ - id: {attr_name}\n+   type: string\n+   brief: Auto-detected attribute",
                    risk_level=EvolutionRisk.MEDIUM,
                    confidence=frequency,
                    proposer_agent=self.agent_id
                )
                patches.append(patch)
        
        return patches
    
    def _check_optimizations(self, convention: Dict) -> List[SemanticPatch]:
        """Check for optimization opportunities"""
        patches = []
        
        # Check for redundant attributes
        attr_names = []
        if 'groups' in convention:
            for group in convention['groups']:
                if 'attributes' in group:
                    for attr in group['attributes']:
                        attr_names.append(attr.get('id'))
        
        # Find similar attribute names that could be consolidated
        for i, name1 in enumerate(attr_names):
            for name2 in attr_names[i+1:]:
                similarity = difflib.SequenceMatcher(None, name1, name2).ratio()
                if similarity > 0.8 and name1 != name2:
                    patch = SemanticPatch(
                        id=f"consolidate-{name1}-{name2}",
                        convention_name=self.convention_path.stem,
                        patch_type="consolidate_attributes",
                        description=f"Consolidate similar attributes: {name1} and {name2}",
                        diff=f"# Consider merging {name1} and {name2}",
                        risk_level=EvolutionRisk.HIGH,
                        confidence=similarity,
                        proposer_agent=self.agent_id
                    )
                    patches.append(patch)
        
        return patches
    
    async def validate_patch(self, patch: SemanticPatch) -> bool:
        """Validate a semantic patch before applying"""
        # Create temporary convention with patch applied
        temp_convention = self._apply_patch_to_convention(patch)
        
        # Generate test spans
        test_spans = self._generate_test_spans(temp_convention)
        
        # Validate with new convention
        results = await self.validator.run_concurrent_validation(test_spans)
        
        # Calculate validation score
        valid_count = sum(1 for r in results if r['valid'])
        validation_score = valid_count / len(results) if results else 0
        
        patch.validation_results = {
            "validation_score": validation_score,
            "total_spans": len(results),
            "valid_spans": valid_count
        }
        
        # Auto-approve low risk patches with high validation
        if patch.risk_level == EvolutionRisk.LOW and validation_score > 0.95:
            patch.approved = True
            logger.info(f"✅ Auto-approved low-risk patch: {patch.id}")
        
        return validation_score > 0.9
    
    def _apply_patch_to_convention(self, patch: SemanticPatch) -> Dict:
        """Apply patch to convention (simulation)"""
        # In production, would properly parse and modify YAML
        with open(self.convention_path) as f:
            convention = yaml.safe_load(f)
        
        # Simple simulation of patch application
        if patch.patch_type == "fix_grammar":
            # Would apply actual grammar fix
            pass
        elif patch.patch_type == "add_attribute":
            # Would add new attribute to appropriate group
            pass
        
        return convention
    
    def _generate_test_spans(self, convention: Dict) -> List[Dict]:
        """Generate test spans for validation"""
        test_spans = []
        
        # Generate spans based on convention
        if 'spans' in convention:
            for span_def in convention['spans']:
                test_span = {
                    "name": span_def.get('span_name', 'test.span'),
                    "attributes": {
                        "test": True,
                        "convention.version": "5.1.0"
                    },
                    "duration": 10
                }
                test_spans.append(test_span)
        
        return test_spans if test_spans else [{"name": "test.span", "attributes": {}, "duration": 1}]


class SemanticEvolutionEngine:
    """Engine for autonomous semantic convention evolution"""
    
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.meta_agents = {}
        self.metrics = EvolutionMetrics()
        self.ci_webhook_url = None  # Would be configured for auto-approval
        
    def register_meta_agent(self, agent_id: str, convention_name: str) -> MetaAgent:
        """Register a meta-agent for a convention"""
        convention_path = self.registry_path / f"{convention_name}.yaml"
        agent = MetaAgent(agent_id, convention_path)
        self.meta_agents[agent_id] = agent
        return agent
    
    async def evolution_cycle(self) -> List[SemanticPatch]:
        """Run one evolution cycle across all meta-agents"""
        all_patches = []
        
        for agent_id, agent in self.meta_agents.items():
            logger.info(f"🧬 Meta-agent {agent_id} analyzing convention...")
            
            # Analyze and propose patches
            patches = await agent.analyze_convention()
            
            # Validate each patch
            for patch in patches:
                valid = await agent.validate_patch(patch)
                if valid:
                    all_patches.append(patch)
                    self.metrics.total_proposals += 1
                    
                    if patch.approved:
                        self.metrics.auto_approved += 1
                        await self.apply_patch(patch)
        
        return all_patches
    
    async def apply_patch(self, patch: SemanticPatch) -> bool:
        """Apply an approved patch to the convention"""
        if not patch.approved:
            logger.warning(f"❌ Cannot apply unapproved patch: {patch.id}")
            return False
        
        try:
            # In production, would:
            # 1. Create Git branch
            # 2. Apply patch to YAML
            # 3. Run full validation suite
            # 4. Create pull request
            # 5. Auto-merge if low risk
            
            logger.info(f"🔧 Applying patch: {patch.id}")
            logger.info(f"   Type: {patch.patch_type}")
            logger.info(f"   Risk: {patch.risk_level.value}")
            logger.info(f"   Description: {patch.description}")
            
            patch.applied = True
            self.metrics.approved_patches += 1
            
            if patch.patch_type == "fix_grammar":
                self.metrics.grammar_fixes += 1
            elif patch.risk_level == EvolutionRisk.HIGH:
                self.metrics.breaking_changes += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply patch {patch.id}: {e}")
            return False
    
    def generate_evolution_report(self) -> Dict[str, Any]:
        """Generate evolution metrics report"""
        return {
            "metrics": {
                "total_proposals": self.metrics.total_proposals,
                "approved_patches": self.metrics.approved_patches,
                "auto_approved": self.metrics.auto_approved,
                "rejection_rate": (
                    self.metrics.rejected_patches / self.metrics.total_proposals 
                    if self.metrics.total_proposals > 0 else 0
                ),
                "grammar_fixes": self.metrics.grammar_fixes,
                "breaking_changes": self.metrics.breaking_changes
            },
            "health": {
                "evolution_active": len(self.meta_agents) > 0,
                "auto_approval_rate": (
                    self.metrics.auto_approved / self.metrics.approved_patches
                    if self.metrics.approved_patches > 0 else 0
                ),
                "safety_score": 1.0 - (
                    self.metrics.breaking_changes / self.metrics.approved_patches
                    if self.metrics.approved_patches > 0 else 1.0
                )
            }
        }