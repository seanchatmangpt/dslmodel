"""
Global Post-Quantum Cryptography Manager
Handles worldwide PQC deployment with regional compliance
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from pydantic import Field, validator
import json

from dslmodel import DSLModel
from .core import (
    PQCAlgorithmType, PQCSecurityLevel, PQCKeyPair,
    PQCSignature, PQCCiphertext, HybridPQCScheme
)
from .algorithms import (
    KyberAlgorithm, DilithiumAlgorithm, 
    FalconAlgorithm, SPHINCSPlusAlgorithm
)

class PQCRegion(str, Enum):
    """Global regions with different PQC requirements"""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    MIDDLE_EAST = "middle_east"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    GLOBAL = "global"

class PQCCompliance(str, Enum):
    """Compliance frameworks for PQC"""
    NIST = "nist"  # US NIST standards
    ETSI = "etsi"  # European standards
    ISO = "iso"    # International standards
    CNSA = "cnsa"  # US NSA Commercial National Security Algorithm
    BSI = "bsi"    # German Federal Office for Information Security
    ANSSI = "anssi" # French cybersecurity agency
    CCCS = "cccs"  # Canadian Centre for Cyber Security

class RegionalPQCPolicy(DSLModel):
    """Regional policy for PQC deployment"""
    region: PQCRegion = Field(..., description="Geographic region")
    compliance_frameworks: List[PQCCompliance] = Field(..., description="Required compliance")
    allowed_algorithms: List[PQCAlgorithmType] = Field(..., description="Permitted algorithms")
    minimum_security_level: PQCSecurityLevel = Field(..., description="Minimum security level")
    hybrid_required_until: Optional[datetime] = Field(None, description="Hybrid mode deadline")
    mandatory_from: datetime = Field(..., description="PQC mandatory date")
    additional_requirements: Dict[str, Any] = Field(default_factory=dict)

class GlobalPQCConfiguration(DSLModel):
    """Global configuration for PQC deployment"""
    default_kem_algorithm: PQCAlgorithmType = Field(PQCAlgorithmType.KYBER)
    default_signature_algorithm: PQCAlgorithmType = Field(PQCAlgorithmType.DILITHIUM)
    default_security_level: PQCSecurityLevel = Field(PQCSecurityLevel.LEVEL_3)
    regional_policies: List[RegionalPQCPolicy] = Field(default_factory=list)
    global_transition_date: datetime = Field(..., description="Global PQC transition date")
    allow_algorithm_negotiation: bool = Field(True, description="Allow algorithm negotiation")
    require_forward_secrecy: bool = Field(True, description="Require forward secrecy")

class PQCKeyStore(DSLModel):
    """Distributed key store for global PQC keys"""
    store_id: str = Field(..., description="Key store identifier")
    region: PQCRegion = Field(..., description="Store region")
    keys: Dict[str, PQCKeyPair] = Field(default_factory=dict, description="Stored keys")
    replication_regions: List[PQCRegion] = Field(default_factory=list)
    last_sync: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_key(self, key: PQCKeyPair) -> None:
        """Add key to store"""
        self.keys[key.key_id] = key
        self.last_sync = datetime.now(timezone.utc)
    
    def get_key(self, key_id: str) -> Optional[PQCKeyPair]:
        """Retrieve key by ID"""
        return self.keys.get(key_id)
    
    def remove_expired_keys(self) -> int:
        """Remove expired keys"""
        expired = [k_id for k_id, key in self.keys.items() if key.is_expired()]
        for k_id in expired:
            del self.keys[k_id]
        return len(expired)

class GlobalPQCManager:
    """Manages global PQC operations with regional compliance"""
    
    def __init__(self, config: GlobalPQCConfiguration):
        self.config = config
        self.providers = {
            PQCAlgorithmType.KYBER: KyberAlgorithm(),
            PQCAlgorithmType.DILITHIUM: DilithiumAlgorithm(),
            PQCAlgorithmType.FALCON: FalconAlgorithm(),
            PQCAlgorithmType.SPHINCS_PLUS: SPHINCSPlusAlgorithm()
        }
        self.key_stores: Dict[PQCRegion, PQCKeyStore] = {}
        self._initialize_regional_stores()
    
    def _initialize_regional_stores(self):
        """Initialize key stores for each region"""
        for region in PQCRegion:
            self.key_stores[region] = PQCKeyStore(
                store_id=f"store-{region.value}",
                region=region
            )
    
    def get_regional_policy(self, region: PQCRegion) -> Optional[RegionalPQCPolicy]:
        """Get policy for specific region"""
        for policy in self.config.regional_policies:
            if policy.region == region:
                return policy
        return None
    
    def select_algorithm(self, 
                        region: PQCRegion,
                        purpose: str = "encryption") -> Tuple[PQCAlgorithmType, PQCSecurityLevel]:
        """Select appropriate algorithm for region and purpose"""
        policy = self.get_regional_policy(region)
        
        if purpose == "encryption":
            # Only Kyber for encryption
            algorithm = PQCAlgorithmType.KYBER
        else:  # signature
            # Select based on regional policy
            if policy:
                # Use first allowed signature algorithm
                for alg in policy.allowed_algorithms:
                    if alg != PQCAlgorithmType.KYBER:
                        algorithm = alg
                        break
                else:
                    algorithm = self.config.default_signature_algorithm
            else:
                algorithm = self.config.default_signature_algorithm
        
        # Determine security level
        security_level = self.config.default_security_level
        if policy and policy.minimum_security_level.value > security_level.value:
            security_level = policy.minimum_security_level
        
        return algorithm, security_level
    
    def generate_regional_keypair(self, region: PQCRegion, purpose: str = "encryption") -> PQCKeyPair:
        """Generate keypair compliant with regional requirements"""
        algorithm, security_level = self.select_algorithm(region, purpose)
        
        provider = self.providers[algorithm]
        keypair = provider.generate_keypair(security_level)
        
        # Add regional metadata
        keypair.metadata.update({
            "region": region.value,
            "purpose": purpose,
            "compliance": self._get_regional_compliance(region)
        })
        
        # Store in regional key store
        self.key_stores[region].add_key(keypair)
        
        # Replicate to other regions if configured
        policy = self.get_regional_policy(region)
        if policy and "replication_regions" in policy.additional_requirements:
            for rep_region in policy.additional_requirements["replication_regions"]:
                if rep_region in self.key_stores:
                    self.key_stores[PQCRegion(rep_region)].add_key(keypair)
        
        return keypair
    
    def _get_regional_compliance(self, region: PQCRegion) -> List[str]:
        """Get compliance frameworks for region"""
        policy = self.get_regional_policy(region)
        if policy:
            return [c.value for c in policy.compliance_frameworks]
        return []
    
    def encrypt_for_region(self, 
                          plaintext: bytes,
                          recipient_key_id: str,
                          sender_region: PQCRegion,
                          recipient_region: PQCRegion) -> PQCCiphertext:
        """Encrypt data for cross-regional transmission"""
        # Find recipient key
        recipient_key = self.key_stores[recipient_region].get_key(recipient_key_id)
        if not recipient_key:
            raise ValueError(f"Recipient key {recipient_key_id} not found in {recipient_region}")
        
        # Check if hybrid mode required
        policy = self.get_regional_policy(sender_region)
        use_hybrid = False
        if policy and policy.hybrid_required_until:
            use_hybrid = datetime.now(timezone.utc) < policy.hybrid_required_until
        
        # Encrypt
        provider = self.providers[recipient_key.algorithm]
        ciphertext = provider.encrypt(plaintext, recipient_key.public_key)
        
        # Add cross-regional metadata
        ciphertext.metadata.update({
            "sender_region": sender_region.value,
            "recipient_region": recipient_region.value,
            "hybrid_mode": use_hybrid,
            "compliance": self._get_regional_compliance(sender_region)
        })
        
        return ciphertext
    
    def verify_regional_compliance(self, 
                                 region: PQCRegion,
                                 algorithm: PQCAlgorithmType,
                                 security_level: PQCSecurityLevel) -> bool:
        """Verify if algorithm/level meets regional requirements"""
        policy = self.get_regional_policy(region)
        if not policy:
            return True  # No policy means any algorithm is allowed
        
        # Check algorithm
        if algorithm not in policy.allowed_algorithms:
            return False
        
        # Check security level
        if security_level.value < policy.minimum_security_level.value:
            return False
        
        # Check timing
        if datetime.now(timezone.utc) >= policy.mandatory_from:
            # PQC is mandatory, classical crypto not allowed
            return True
        
        return True
    
    def get_global_readiness_report(self) -> Dict[str, Any]:
        """Generate global PQC readiness report"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "global_transition_date": self.config.global_transition_date.isoformat(),
            "regions": {}
        }
        
        for region in PQCRegion:
            policy = self.get_regional_policy(region)
            key_count = len(self.key_stores[region].keys)
            
            region_info = {
                "key_count": key_count,
                "policy_defined": policy is not None
            }
            
            if policy:
                region_info.update({
                    "mandatory_from": policy.mandatory_from.isoformat(),
                    "compliance_frameworks": [c.value for c in policy.compliance_frameworks],
                    "allowed_algorithms": [a.value for a in policy.allowed_algorithms],
                    "minimum_security_level": policy.minimum_security_level.value,
                    "is_mandatory": datetime.now(timezone.utc) >= policy.mandatory_from
                })
            
            report["regions"][region.value] = region_info
        
        # Calculate global readiness percentage
        total_regions = len(PQCRegion)
        ready_regions = sum(1 for r in report["regions"].values() 
                          if r.get("is_mandatory", False) or r["key_count"] > 0)
        report["global_readiness_percentage"] = (ready_regions / total_regions) * 100
        
        return report

# Default regional policies
def create_default_regional_policies() -> List[RegionalPQCPolicy]:
    """Create default PQC policies for different regions"""
    return [
        RegionalPQCPolicy(
            region=PQCRegion.NORTH_AMERICA,
            compliance_frameworks=[PQCCompliance.NIST, PQCCompliance.CNSA],
            allowed_algorithms=[
                PQCAlgorithmType.KYBER,
                PQCAlgorithmType.DILITHIUM,
                PQCAlgorithmType.FALCON,
                PQCAlgorithmType.SPHINCS_PLUS
            ],
            minimum_security_level=PQCSecurityLevel.LEVEL_3,
            hybrid_required_until=datetime(2025, 1, 1, tzinfo=timezone.utc),
            mandatory_from=datetime(2030, 1, 1, tzinfo=timezone.utc),
            additional_requirements={"fips_validation": True}
        ),
        RegionalPQCPolicy(
            region=PQCRegion.EUROPE,
            compliance_frameworks=[PQCCompliance.ETSI, PQCCompliance.BSI, PQCCompliance.ANSSI],
            allowed_algorithms=[
                PQCAlgorithmType.KYBER,
                PQCAlgorithmType.DILITHIUM,
                PQCAlgorithmType.FALCON
            ],
            minimum_security_level=PQCSecurityLevel.LEVEL_3,
            hybrid_required_until=datetime(2025, 6, 1, tzinfo=timezone.utc),
            mandatory_from=datetime(2029, 1, 1, tzinfo=timezone.utc),
            additional_requirements={"gdpr_compliant": True}
        ),
        RegionalPQCPolicy(
            region=PQCRegion.ASIA_PACIFIC,
            compliance_frameworks=[PQCCompliance.ISO],
            allowed_algorithms=[
                PQCAlgorithmType.KYBER,
                PQCAlgorithmType.DILITHIUM,
                PQCAlgorithmType.SPHINCS_PLUS
            ],
            minimum_security_level=PQCSecurityLevel.LEVEL_2,
            mandatory_from=datetime(2028, 1, 1, tzinfo=timezone.utc),
            additional_requirements={"multi_language_support": True}
        )
    ]