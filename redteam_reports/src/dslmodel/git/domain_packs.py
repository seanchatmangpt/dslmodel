"""
Domain Pack Submodule System
Manages external domain packs as Git submodules for federation
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import aiofiles

from .git_auto import add_domain_pack, update_submodules, add_notes


@dataclass
class DomainPack:
    """Represents a domain pack configuration."""
    name: str
    url: str
    path: str
    domain: str
    version: str
    description: str
    maintainer: str
    dependencies: List[str]
    semantic_conventions: List[str]
    weaver_templates: List[str]
    last_updated: Optional[str] = None
    commit_sha: Optional[str] = None


@dataclass
class DomainPackRegistry:
    """Registry of available domain packs."""
    packs: Dict[str, DomainPack]
    federation_remotes: List[str]
    last_sync: Optional[str] = None


class DomainPackManager:
    """Manages domain pack submodules and federation."""
    
    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            base_path = Path.cwd()
        
        self.base_path = base_path
        self.domain_packs_dir = base_path / "domain_packs"
        self.registry_file = base_path / "domain_pack_registry.yaml"
        self.registry: Optional[DomainPackRegistry] = None
        
        # Ensure domain_packs directory exists
        self.domain_packs_dir.mkdir(exist_ok=True)
    
    async def load_registry(self) -> DomainPackRegistry:
        """Load domain pack registry from file."""
        if self.registry_file.exists():
            async with aiofiles.open(self.registry_file, 'r') as f:
                content = await f.read()
                registry_data = yaml.safe_load(content)
                
                packs = {}
                for pack_name, pack_data in registry_data.get('packs', {}).items():
                    packs[pack_name] = DomainPack(**pack_data)
                
                self.registry = DomainPackRegistry(
                    packs=packs,
                    federation_remotes=registry_data.get('federation_remotes', []),
                    last_sync=registry_data.get('last_sync')
                )
        else:
            self.registry = DomainPackRegistry(
                packs={},
                federation_remotes=[],
                last_sync=None
            )
        
        return self.registry
    
    async def save_registry(self):
        """Save domain pack registry to file."""
        if not self.registry:
            return
        
        registry_data = {
            'packs': {name: asdict(pack) for name, pack in self.registry.packs.items()},
            'federation_remotes': self.registry.federation_remotes,
            'last_sync': self.registry.last_sync
        }
        
        async with aiofiles.open(self.registry_file, 'w') as f:
            await f.write(yaml.dump(registry_data, default_flow_style=False))
    
    async def discover_available_packs(self, federation_urls: List[str]) -> List[DomainPack]:
        """Discover available domain packs from federation remotes."""
        discovered_packs = []
        
        for url in federation_urls:
            try:
                # Clone/fetch the federation registry
                temp_dir = self.base_path / "temp_federation_discovery"
                temp_dir.mkdir(exist_ok=True)
                
                # Use git to fetch registry information
                # This would typically fetch from a known federation registry
                # For now, simulate with example packs
                
                if "energy" in url.lower():
                    discovered_packs.append(DomainPack(
                        name="energy-pack",
                        url=url,
                        path=f"domain_packs/energy",
                        domain="energy",
                        version="1.0.0",
                        description="Energy domain semantic conventions and templates",
                        maintainer="energy-consortium",
                        dependencies=[],
                        semantic_conventions=["energy.production", "energy.consumption", "energy.grid"],
                        weaver_templates=["energy_dashboard.j2", "energy_metrics.j2"]
                    ))
                
                elif "healthcare" in url.lower():
                    discovered_packs.append(DomainPack(
                        name="healthcare-pack",
                        url=url,
                        path=f"domain_packs/healthcare",
                        domain="healthcare",
                        version="2.1.0",
                        description="Healthcare FHIR and HL7 domain templates",
                        maintainer="healthcare-standards",
                        dependencies=["fhir-base"],
                        semantic_conventions=["healthcare.patient", "healthcare.encounter", "healthcare.medication"],
                        weaver_templates=["fhir_patient.j2", "hl7_message.j2"]
                    ))
                
                elif "finance" in url.lower():
                    discovered_packs.append(DomainPack(
                        name="finance-pack",
                        url=url,
                        path=f"domain_packs/finance",
                        domain="finance",
                        version="1.5.2",
                        description="Financial trading and risk management domain",
                        maintainer="fintech-collective",
                        dependencies=["market-data"],
                        semantic_conventions=["finance.trade", "finance.risk", "finance.compliance"],
                        weaver_templates=["trade_report.j2", "risk_dashboard.j2"]
                    ))
                
            except Exception as e:
                print(f"Failed to discover packs from {url}: {e}")
        
        return discovered_packs
    
    async def install_domain_pack(self, pack: DomainPack, force: bool = False) -> Dict[str, Any]:
        """Install a domain pack as a submodule."""
        if not force and pack.name in (self.registry.packs if self.registry else {}):
            return {
                "success": False,
                "error": f"Domain pack '{pack.name}' already installed"
            }
        
        try:
            # Add as submodule
            result = await add_domain_pack(pack.url, pack.name, str(self.base_path))
            
            if result["success"]:
                # Update registry
                if not self.registry:
                    await self.load_registry()
                
                pack.last_updated = datetime.now().isoformat()
                self.registry.packs[pack.name] = pack
                await self.save_registry()
                
                # Add installation notes
                await add_notes(
                    "domain_pack_install",
                    f"Installed domain pack: {pack.name} v{pack.version}",
                    "HEAD",
                    str(self.base_path)
                )
                
                return {
                    "success": True,
                    "message": f"Domain pack '{pack.name}' installed successfully",
                    "pack": asdict(pack)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to install submodule: {result.get('stderr', 'Unknown error')}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Installation failed: {str(e)}"
            }
    
    async def update_domain_pack(self, pack_name: str) -> Dict[str, Any]:
        """Update a specific domain pack to latest version."""
        if not self.registry or pack_name not in self.registry.packs:
            return {
                "success": False,
                "error": f"Domain pack '{pack_name}' not found"
            }
        
        try:
            pack = self.registry.packs[pack_name]
            pack_path = self.base_path / pack.path
            
            if not pack_path.exists():
                return {
                    "success": False,
                    "error": f"Domain pack path not found: {pack_path}"
                }
            
            # Update submodule
            result = await update_submodules(str(self.base_path))
            
            if result["success"]:
                pack.last_updated = datetime.now().isoformat()
                await self.save_registry()
                
                # Add update notes
                await add_notes(
                    "domain_pack_update",
                    f"Updated domain pack: {pack_name}",
                    "HEAD",
                    str(self.base_path)
                )
                
                return {
                    "success": True,
                    "message": f"Domain pack '{pack_name}' updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to update submodule: {result.get('stderr', 'Unknown error')}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Update failed: {str(e)}"
            }
    
    async def update_all_domain_packs(self) -> Dict[str, Any]:
        """Update all installed domain packs."""
        if not self.registry or not self.registry.packs:
            return {
                "success": True,
                "message": "No domain packs to update"
            }
        
        results = {}
        for pack_name in self.registry.packs.keys():
            results[pack_name] = await self.update_domain_pack(pack_name)
        
        successful_updates = sum(1 for r in results.values() if r["success"])
        total_packs = len(results)
        
        return {
            "success": successful_updates == total_packs,
            "message": f"Updated {successful_updates}/{total_packs} domain packs",
            "results": results
        }
    
    async def remove_domain_pack(self, pack_name: str) -> Dict[str, Any]:
        """Remove a domain pack (submodule deinit)."""
        if not self.registry or pack_name not in self.registry.packs:
            return {
                "success": False,
                "error": f"Domain pack '{pack_name}' not found"
            }
        
        try:
            pack = self.registry.packs[pack_name]
            
            # Deinitialize submodule
            deinit_cmd = f"git submodule deinit -f {pack.path}"
            process = await asyncio.create_subprocess_shell(
                deinit_cmd,
                cwd=str(self.base_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Remove from registry
                del self.registry.packs[pack_name]
                await self.save_registry()
                
                # Add removal notes
                await add_notes(
                    "domain_pack_remove",
                    f"Removed domain pack: {pack_name}",
                    "HEAD",
                    str(self.base_path)
                )
                
                return {
                    "success": True,
                    "message": f"Domain pack '{pack_name}' removed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to remove submodule: {stderr.decode()}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Removal failed: {str(e)}"
            }
    
    async def list_installed_packs(self) -> List[Dict[str, Any]]:
        """List all installed domain packs."""
        if not self.registry:
            await self.load_registry()
        
        if not self.registry.packs:
            return []
        
        return [asdict(pack) for pack in self.registry.packs.values()]
    
    async def get_pack_info(self, pack_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific pack."""
        if not self.registry:
            await self.load_registry()
        
        if not self.registry or pack_name not in self.registry.packs:
            return None
        
        pack = self.registry.packs[pack_name]
        pack_info = asdict(pack)
        
        # Add runtime information
        pack_path = self.base_path / pack.path
        pack_info["installed"] = pack_path.exists()
        pack_info["local_path"] = str(pack_path)
        
        # Check for semantic conventions
        semconv_path = pack_path / "semantic_conventions"
        if semconv_path.exists():
            pack_info["available_semconvs"] = [
                f.stem for f in semconv_path.glob("*.yaml")
            ]
        
        # Check for weaver templates
        templates_path = pack_path / "weaver" / "templates"
        if templates_path.exists():
            pack_info["available_templates"] = [
                f.name for f in templates_path.glob("*.j2")
            ]
        
        return pack_info
    
    async def sync_federation_registry(self, federation_urls: List[str]) -> Dict[str, Any]:
        """Sync with federation registries to discover new packs."""
        try:
            discovered_packs = await self.discover_available_packs(federation_urls)
            
            if not self.registry:
                await self.load_registry()
            
            # Update federation remotes
            self.registry.federation_remotes = federation_urls
            self.registry.last_sync = datetime.now().isoformat()
            
            # Track new discoveries
            new_packs = []
            for pack in discovered_packs:
                if pack.name not in self.registry.packs:
                    new_packs.append(pack)
            
            await self.save_registry()
            
            return {
                "success": True,
                "message": f"Discovered {len(discovered_packs)} packs ({len(new_packs)} new)",
                "discovered_packs": [asdict(p) for p in discovered_packs],
                "new_packs": [asdict(p) for p in new_packs]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Federation sync failed: {str(e)}"
            }


# =============================================================================
# High-level domain pack operations
# =============================================================================

async def install_energy_domain_pack(base_path: Optional[Path] = None) -> Dict[str, Any]:
    """Install the energy domain pack."""
    manager = DomainPackManager(base_path)
    
    energy_pack = DomainPack(
        name="energy",
        url="https://github.com/energy-consortium/energy-domain-pack",
        path="domain_packs/energy",
        domain="energy",
        version="1.0.0",
        description="Energy domain semantic conventions and templates",
        maintainer="energy-consortium",
        dependencies=[],
        semantic_conventions=["energy.production", "energy.consumption", "energy.grid"],
        weaver_templates=["energy_dashboard.j2", "energy_metrics.j2"]
    )
    
    return await manager.install_domain_pack(energy_pack)


async def install_healthcare_domain_pack(base_path: Optional[Path] = None) -> Dict[str, Any]:
    """Install the healthcare domain pack."""
    manager = DomainPackManager(base_path)
    
    healthcare_pack = DomainPack(
        name="healthcare",
        url="https://github.com/healthcare-standards/healthcare-domain-pack",
        path="domain_packs/healthcare",
        domain="healthcare",
        version="2.1.0",
        description="Healthcare FHIR and HL7 domain templates",
        maintainer="healthcare-standards",
        dependencies=["fhir-base"],
        semantic_conventions=["healthcare.patient", "healthcare.encounter", "healthcare.medication"],
        weaver_templates=["fhir_patient.j2", "hl7_message.j2"]
    )
    
    return await manager.install_domain_pack(healthcare_pack)


async def setup_federation_workspace(
    federation_urls: List[str], 
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Setup a complete federation workspace with multiple domain packs."""
    manager = DomainPackManager(base_path)
    
    # Sync with federation registries
    sync_result = await manager.sync_federation_registry(federation_urls)
    
    if not sync_result["success"]:
        return sync_result
    
    # Install discovered packs
    install_results = {}
    for pack_data in sync_result.get("new_packs", []):
        pack = DomainPack(**pack_data)
        install_results[pack.name] = await manager.install_domain_pack(pack)
    
    successful_installs = sum(1 for r in install_results.values() if r["success"])
    total_installs = len(install_results)
    
    return {
        "success": True,
        "message": f"Federation workspace setup complete. Installed {successful_installs}/{total_installs} domain packs",
        "sync_result": sync_result,
        "install_results": install_results
    }