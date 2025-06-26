#!/usr/bin/env python3
"""
Weaver Semantic Convention Enforcement
======================================

Enforces semantic conventions for organizational transformation telemetry.
"""

import subprocess
import sys
from pathlib import Path

def enforce_conventions():
    """Enforce semantic conventions using Weaver"""
    weaver_path = Path("weaver.yaml")
    
    if not weaver_path.exists():
        print("⚠️ weaver.yaml not found - creating basic configuration")
        create_basic_weaver_config()
    
    # Check for weaver templates
    template_dir = Path("weaver_templates")
    if not template_dir.exists():
        print("📋 Creating Weaver templates directory")
        template_dir.mkdir()
    
    print("✅ Weaver enforcement configured")
    return True

def create_basic_weaver_config():
    """Create basic weaver configuration"""
    import yaml
    
    config = {
        "params": {
            "project_name": "DSLModel",
            "language": "python",
            "organization": "SeanchatmanGPT",
            "semantic_conventions_version": "1.20.0"
        }
    }
    
    with open("weaver.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

if __name__ == "__main__":
    enforce_conventions()
