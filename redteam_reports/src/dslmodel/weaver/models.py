"""Models for semantic convention definitions."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .enums import AttrType, Cardinality, SpanKind


@dataclass
class Attribute:
    """Represents an attribute in a semantic convention."""
    name: str
    type: AttrType
    description: str
    cardinality: Cardinality = Cardinality.optional
    examples: Optional[List[Any]] = None
    ref: Optional[str] = None
    tag: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML generation."""
        result = {
            "id": self.name,
            "type": self.type.value,
            "brief": self.description,
            "requirement_level": self.cardinality.value,
        }
        
        if self.examples:
            result["examples"] = self.examples
            
        if self.ref:
            result["ref"] = self.ref
            
        if self.tag:
            result["tag"] = self.tag
            
        return result


@dataclass
class Span:
    """Represents a span definition in a semantic convention."""
    name: str
    brief: str
    kind: SpanKind = SpanKind.internal
    attributes: List[Attribute] = field(default_factory=list)
    prefix: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML generation."""
        result = {
            "id": self.name,
            "brief": self.brief,
            "type": "span",
            "span_kind": self.kind.value,
        }
        
        if self.prefix:
            result["prefix"] = self.prefix
        else:
            # Extract prefix from name
            parts = self.name.split(".")
            if len(parts) > 1:
                result["prefix"] = ".".join(parts[:-1])
                
        if self.attributes:
            result["attributes"] = [attr.to_dict() for attr in self.attributes]
            
        return result


@dataclass 
class ConventionSet:
    """Represents a set of semantic conventions."""
    title: str
    version: str
    spans: List[Span] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)
    
    def to_yaml_groups(self) -> List[Dict[str, Any]]:
        """Convert to YAML groups format expected by Weaver."""
        groups = []
        
        # Add span groups
        for span in self.spans:
            groups.append(span.to_dict())
            
        # Add attribute groups if any
        if self.attributes:
            attr_group = {
                "id": f"{self.title.lower().replace(' ', '_')}_attributes",
                "type": "attribute_group",
                "brief": f"Attributes for {self.title}",
                "attributes": [attr.to_dict() for attr in self.attributes]
            }
            groups.append(attr_group)
            
        return groups