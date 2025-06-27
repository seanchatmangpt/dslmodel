"""
Scrum at Scale - Git-native Multi-team Coordination
====================================================

Implements Scrum at Scale framework using pure git primitives for
coordinating multiple Scrum teams with shared dependencies and
synchronized ceremonies.
"""

import json
import datetime
import subprocess
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

try:
    from ..utils.span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from ..utils.git_auto import execute_git_command, notes_add, tag, worktree_add
except ImportError:
    def execute_git_command(op, **kwargs):
        print(f"[GIT] Would execute: {op} with {kwargs}")
        return type('Result', (), {'returncode': 0, 'stdout': 'success'})()
    def notes_add(ref, target, message):
        print(f"[GIT] Would add note: {ref} -> {target}: {message}")
    def tag(name, message):
        print(f"[GIT] Would create tag: {name} with {message}")
    def worktree_add(path, sha):
        print(f"[GIT] Would add worktree: {path} -> {sha}")

try:
    from ..utils.log_tools import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

class ScaleLevel(Enum):
    """Scrum at Scale organizational levels."""
    TEAM = "team"
    PROGRAM = "program" 
    PORTFOLIO = "portfolio"
    ENTERPRISE = "enterprise"

class CeremonyType(Enum):
    """Types of scaled ceremonies."""
    SCRUM_OF_SCRUMS = "scrum_of_scrums"
    SCALED_PLANNING = "scaled_planning"
    SCALED_REVIEW = "scaled_review"
    SCALED_RETROSPECTIVE = "scaled_retrospective"
    METASCRUM = "metascrum"

@dataclass
class ScaledTeam:
    """Represents a team in Scrum at Scale."""
    id: str
    name: str
    level: ScaleLevel
    parent_team: Optional[str]
    child_teams: List[str]
    git_worktree: str
    sprint_prefix: str
    members: List[str]
    created_at: str

@dataclass
class Dependency:
    """Represents a cross-team dependency."""
    id: str
    from_team: str
    to_team: str
    description: str
    status: str  # blocked, in_progress, resolved
    sprint_target: str
    git_issue: Optional[int]
    created_at: str

@dataclass
class ScaledCeremony:
    """Represents a scaled Scrum ceremony."""
    id: str
    type: CeremonyType
    level: ScaleLevel
    participants: List[str]  # Team IDs
    schedule: str
    git_branch: str
    notes_ref: str
    created_at: str

class ScrumAtScale:
    """Git-native implementation of Scrum at Scale framework."""
    
    def __init__(self, organization_name: str = "default"):
        self.organization = organization_name
        self.teams: Dict[str, ScaledTeam] = {}
        self.dependencies: Dict[str, Dependency] = {}
        self.ceremonies: Dict[str, ScaledCeremony] = {}
        self.worktree_base = Path("scrum_scale_worktrees")
        self.worktree_base.mkdir(exist_ok=True)
        
        # Initialize organizational structure
        self._create_organizational_structure()
    
    def _create_organizational_structure(self):
        """Create git-based organizational structure."""
        try:
            # Create organizational branches
            for level in ScaleLevel:
                branch_name = f"scrum-scale/{level.value}"
                try:
                    subprocess.run(
                        ["git", "checkout", "-b", branch_name],
                        capture_output=True, check=False
                    )
                    subprocess.run(
                        ["git", "checkout", "main"],
                        capture_output=True, check=False
                    )
                except:
                    pass  # Branch might already exist
            
            logger.info("Organizational git structure initialized")
        except Exception as e:
            logger.warning(f"Could not initialize git structure: {e}")
    
    @span("scrum_scale_create_team")
    def create_team(
        self,
        team_id: str,
        name: str,
        level: ScaleLevel,
        parent_team: Optional[str] = None,
        members: Optional[List[str]] = None
    ) -> str:
        """Create a new scaled team with git worktree."""
        
        if team_id in self.teams:
            raise ValueError(f"Team {team_id} already exists")
        
        # Create git worktree for team
        worktree_path = self.worktree_base / team_id
        git_branch = f"scrum-scale/{level.value}/{team_id}"
        
        try:
            # Create branch for team
            subprocess.run(
                ["git", "checkout", "-b", git_branch],
                capture_output=True, check=False
            )
            
            # Create worktree
            worktree_add(str(worktree_path), git_branch)
            
            subprocess.run(
                ["git", "checkout", "main"],
                capture_output=True, check=False
            )
            
        except Exception as e:
            logger.warning(f"Git worktree creation failed: {e}")
        
        # Create team configuration
        team = ScaledTeam(
            id=team_id,
            name=name,
            level=level,
            parent_team=parent_team,
            child_teams=[],
            git_worktree=str(worktree_path),
            sprint_prefix=f"SP-{team_id}",
            members=members or [],
            created_at=datetime.datetime.now().isoformat()
        )
        
        # Update parent-child relationships
        if parent_team and parent_team in self.teams:
            self.teams[parent_team].child_teams.append(team_id)
        
        self.teams[team_id] = team
        
        # Create team metadata tag
        metadata = {
            "team_id": team_id,
            "name": name,
            "level": level.value,
            "parent_team": parent_team,
            "git_worktree": str(worktree_path),
            "created_at": team.created_at,
            "scrum_at_scale": True
        }
        
        tag(f"team/{team_id}/created", json.dumps(metadata, indent=2))
        
        logger.info(f"🏗️ Created scaled team: {team_id} ({level.value})")
        return team_id
    
    @span("scrum_scale_create_dependency")
    def create_dependency(
        self,
        from_team: str,
        to_team: str,
        description: str,
        sprint_target: str
    ) -> str:
        """Create a cross-team dependency."""
        
        if from_team not in self.teams or to_team not in self.teams:
            raise ValueError("Both teams must exist to create dependency")
        
        dep_id = f"DEP-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        dependency = Dependency(
            id=dep_id,
            from_team=from_team,
            to_team=to_team,
            description=description,
            status="blocked",
            sprint_target=sprint_target,
            git_issue=None,  # Could create actual git issue
            created_at=datetime.datetime.now().isoformat()
        )
        
        self.dependencies[dep_id] = dependency
        
        # Create dependency tracking tag
        dep_data = {
            "dependency_id": dep_id,
            "from_team": from_team,
            "to_team": to_team,
            "description": description,
            "status": dependency.status,
            "sprint_target": sprint_target,
            "created_at": dependency.created_at
        }
        
        tag(f"dependency/{dep_id}/created", json.dumps(dep_data, indent=2))
        
        # Add notes to both teams
        notes_add(
            "dependencies",
            f"team/{from_team}/created",
            f"Dependency {dep_id} created: {description} (to {to_team})"
        )
        notes_add(
            "dependencies", 
            f"team/{to_team}/created",
            f"Dependency {dep_id} received: {description} (from {from_team})"
        )
        
        logger.info(f"🔗 Created dependency: {dep_id} ({from_team} -> {to_team})")
        return dep_id
    
    @span("scrum_scale_schedule_ceremony")
    def schedule_ceremony(
        self,
        ceremony_type: CeremonyType,
        level: ScaleLevel,
        participants: List[str],
        schedule: str
    ) -> str:
        """Schedule a scaled Scrum ceremony."""
        
        ceremony_id = f"CER-{ceremony_type.value}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"
        
        # Create git branch for ceremony
        ceremony_branch = f"ceremony/{level.value}/{ceremony_type.value}/{ceremony_id}"
        
        try:
            subprocess.run(
                ["git", "checkout", "-b", ceremony_branch],
                capture_output=True, check=False
            )
            subprocess.run(
                ["git", "checkout", "main"],
                capture_output=True, check=False
            )
        except:
            pass
        
        ceremony = ScaledCeremony(
            id=ceremony_id,
            type=ceremony_type,
            level=level,
            participants=participants,
            schedule=schedule,
            git_branch=ceremony_branch,
            notes_ref=f"ceremony_{ceremony_type.value}",
            created_at=datetime.datetime.now().isoformat()
        )
        
        self.ceremonies[ceremony_id] = ceremony
        
        # Create ceremony metadata tag
        ceremony_data = {
            "ceremony_id": ceremony_id,
            "type": ceremony_type.value,
            "level": level.value,
            "participants": participants,
            "schedule": schedule,
            "git_branch": ceremony_branch,
            "created_at": ceremony.created_at
        }
        
        tag(f"ceremony/{ceremony_id}/scheduled", json.dumps(ceremony_data, indent=2))
        
        logger.info(f"📅 Scheduled ceremony: {ceremony_id} ({ceremony_type.value})")
        return ceremony_id
    
    @span("scrum_scale_conduct_scrum_of_scrums")
    def conduct_scrum_of_scrums(
        self,
        program_teams: List[str],
        facilitator: str
    ) -> Dict[str, Any]:
        """Conduct a Scrum of Scrums ceremony."""
        
        ceremony_id = self.schedule_ceremony(
            CeremonyType.SCRUM_OF_SCRUMS,
            ScaleLevel.PROGRAM,
            program_teams,
            datetime.datetime.now().isoformat()
        )
        
        # Collect status from each team
        team_statuses = {}
        cross_team_impediments = []
        
        for team_id in program_teams:
            if team_id in self.teams:
                team = self.teams[team_id]
                
                # Get team's latest sprint status (mock for now)
                status = {
                    "team_id": team_id,
                    "current_sprint": f"{team.sprint_prefix}-current",
                    "progress": "on_track",
                    "completed_stories": 8,
                    "remaining_stories": 4,
                    "impediments": [],
                    "dependencies_status": []
                }
                
                # Check dependencies for this team
                team_deps = [d for d in self.dependencies.values() 
                           if d.from_team == team_id or d.to_team == team_id]
                
                for dep in team_deps:
                    if dep.status == "blocked":
                        impediment = {
                            "type": "dependency",
                            "description": dep.description,
                            "blocking_team": dep.to_team if dep.from_team == team_id else dep.from_team,
                            "dependency_id": dep.id
                        }
                        cross_team_impediments.append(impediment)
                        status["dependencies_status"].append(f"Blocked: {dep.description}")
                
                team_statuses[team_id] = status
        
        # Create Scrum of Scrums summary
        sos_summary = {
            "ceremony_id": ceremony_id,
            "type": "scrum_of_scrums",
            "facilitator": facilitator,
            "participants": program_teams,
            "conducted_at": datetime.datetime.now().isoformat(),
            "team_statuses": team_statuses,
            "cross_team_impediments": cross_team_impediments,
            "action_items": [],
            "next_meeting": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        }
        
        # Record ceremony notes
        ceremony = self.ceremonies[ceremony_id]
        notes_add(
            ceremony.notes_ref,
            f"ceremony/{ceremony_id}/scheduled",
            json.dumps(sos_summary, indent=2)
        )
        
        logger.info(f"🔄 Conducted Scrum of Scrums: {ceremony_id}")
        return sos_summary
    
    @span("scrum_scale_sync_sprints")
    def sync_sprints(self, teams: List[str], sync_cadence: str = "2_weeks") -> Dict[str, Any]:
        """Synchronize sprints across multiple teams."""
        
        sync_id = f"SYNC-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"
        
        # Calculate sync points
        sync_start = datetime.datetime.now()
        if sync_cadence == "2_weeks":
            sync_end = sync_start + datetime.timedelta(weeks=2)
        elif sync_cadence == "3_weeks":
            sync_end = sync_start + datetime.timedelta(weeks=3)
        else:
            sync_end = sync_start + datetime.timedelta(weeks=2)
        
        # Create synchronized sprint tags for all teams
        sync_data = {
            "sync_id": sync_id,
            "teams": teams,
            "sync_start": sync_start.isoformat(),
            "sync_end": sync_end.isoformat(),
            "cadence": sync_cadence,
            "synchronized_sprints": {}
        }
        
        for team_id in teams:
            if team_id in self.teams:
                team = self.teams[team_id]
                sprint_id = f"{team.sprint_prefix}-{sync_id}"
                
                sprint_data = {
                    "sprint_id": sprint_id,
                    "team_id": team_id,
                    "start_date": sync_start.isoformat(),
                    "end_date": sync_end.isoformat(),
                    "synchronized": True,
                    "sync_group": sync_id
                }
                
                # Create synchronized sprint tag
                tag(f"sprint/{sprint_id}/sync", json.dumps(sprint_data, indent=2))
                
                sync_data["synchronized_sprints"][team_id] = sprint_data
        
        # Create overall sync tag
        tag(f"sync/{sync_id}/created", json.dumps(sync_data, indent=2))
        
        logger.info(f"🔄 Synchronized sprints: {sync_id} for {len(teams)} teams")
        return sync_data
    
    @span("scrum_scale_resolve_dependency")
    def resolve_dependency(self, dependency_id: str, resolver: str) -> bool:
        """Mark a cross-team dependency as resolved."""
        
        if dependency_id not in self.dependencies:
            logger.error(f"Dependency {dependency_id} not found")
            return False
        
        dependency = self.dependencies[dependency_id]
        dependency.status = "resolved"
        
        # Create resolution tag
        resolution_data = {
            "dependency_id": dependency_id,
            "resolved_by": resolver,
            "resolved_at": datetime.datetime.now().isoformat(),
            "original_description": dependency.description,
            "from_team": dependency.from_team,
            "to_team": dependency.to_team
        }
        
        tag(f"dependency/{dependency_id}/resolved", json.dumps(resolution_data, indent=2))
        
        # Add resolution notes to both teams
        notes_add(
            "dependencies",
            f"team/{dependency.from_team}/created",
            f"Dependency {dependency_id} RESOLVED by {resolver}"
        )
        notes_add(
            "dependencies",
            f"team/{dependency.to_team}/created", 
            f"Dependency {dependency_id} RESOLVED by {resolver}"
        )
        
        logger.info(f"✅ Resolved dependency: {dependency_id}")
        return True
    
    @span("scrum_scale_generate_metrics")
    def generate_scaled_metrics(self) -> Dict[str, Any]:
        """Generate metrics across all scaled teams."""
        
        metrics = {
            "organization": self.organization,
            "generated_at": datetime.datetime.now().isoformat(),
            "teams": {
                "total": len(self.teams),
                "by_level": {},
                "team_details": {}
            },
            "dependencies": {
                "total": len(self.dependencies),
                "by_status": {},
                "dependency_details": {}
            },
            "ceremonies": {
                "total": len(self.ceremonies),
                "by_type": {},
                "ceremony_details": {}
            },
            "health_indicators": {}
        }
        
        # Team metrics by level
        for team_id, team in self.teams.items():
            level = team.level.value
            metrics["teams"]["by_level"][level] = metrics["teams"]["by_level"].get(level, 0) + 1
            
            metrics["teams"]["team_details"][team_id] = {
                "name": team.name,
                "level": level,
                "members": len(team.members),
                "child_teams": len(team.child_teams)
            }
        
        # Dependency metrics
        for dep_id, dep in self.dependencies.items():
            status = dep.status
            metrics["dependencies"]["by_status"][status] = metrics["dependencies"]["by_status"].get(status, 0) + 1
            
            metrics["dependencies"]["dependency_details"][dep_id] = {
                "from_team": dep.from_team,
                "to_team": dep.to_team,
                "status": status,
                "description": dep.description
            }
        
        # Ceremony metrics
        for cer_id, cer in self.ceremonies.items():
            cer_type = cer.type.value
            metrics["ceremonies"]["by_type"][cer_type] = metrics["ceremonies"]["by_type"].get(cer_type, 0) + 1
            
            metrics["ceremonies"]["ceremony_details"][cer_id] = {
                "type": cer_type,
                "level": cer.level.value,
                "participants": len(cer.participants)
            }
        
        # Calculate health indicators
        total_deps = len(self.dependencies)
        blocked_deps = len([d for d in self.dependencies.values() if d.status == "blocked"])
        
        metrics["health_indicators"] = {
            "dependency_health": 1.0 - (blocked_deps / total_deps) if total_deps > 0 else 1.0,
            "team_structure_health": 1.0,  # Could add more sophisticated metrics
            "ceremony_coverage": len(self.ceremonies) / len(self.teams) if len(self.teams) > 0 else 0.0
        }
        
        return metrics

# Convenience functions for common scaled operations

@span("scrum_scale_bootstrap_organization")
def bootstrap_scaled_organization(org_name: str) -> ScrumAtScale:
    """Bootstrap a complete Scrum at Scale organization."""
    
    scrum_scale = ScrumAtScale(org_name)
    
    # Create enterprise team
    enterprise_id = scrum_scale.create_team(
        "enterprise-001",
        "Enterprise Leadership Team",
        ScaleLevel.ENTERPRISE,
        members=["ceo@company.com", "cto@company.com"]
    )
    
    # Create portfolio teams
    portfolio1_id = scrum_scale.create_team(
        "portfolio-product",
        "Product Portfolio Team", 
        ScaleLevel.PORTFOLIO,
        parent_team=enterprise_id,
        members=["product.head@company.com", "arch.lead@company.com"]
    )
    
    portfolio2_id = scrum_scale.create_team(
        "portfolio-platform",
        "Platform Portfolio Team",
        ScaleLevel.PORTFOLIO, 
        parent_team=enterprise_id,
        members=["platform.head@company.com", "devops.lead@company.com"]
    )
    
    # Create program teams
    program1_id = scrum_scale.create_team(
        "program-frontend",
        "Frontend Program Team",
        ScaleLevel.PROGRAM,
        parent_team=portfolio1_id,
        members=["frontend.lead@company.com"]
    )
    
    program2_id = scrum_scale.create_team(
        "program-backend", 
        "Backend Program Team",
        ScaleLevel.PROGRAM,
        parent_team=portfolio1_id,
        members=["backend.lead@company.com"]
    )
    
    # Create delivery teams
    scrum_scale.create_team(
        "team-ui",
        "UI Development Team",
        ScaleLevel.TEAM,
        parent_team=program1_id,
        members=["ui.dev1@company.com", "ui.dev2@company.com", "ui.po@company.com"]
    )
    
    scrum_scale.create_team(
        "team-api",
        "API Development Team", 
        ScaleLevel.TEAM,
        parent_team=program2_id,
        members=["api.dev1@company.com", "api.dev2@company.com", "api.po@company.com"]
    )
    
    # Create some dependencies
    scrum_scale.create_dependency(
        "team-ui",
        "team-api", 
        "Authentication API for login flow",
        "SP-team-ui-2025-01"
    )
    
    # Schedule regular ceremonies
    scrum_scale.schedule_ceremony(
        CeremonyType.SCRUM_OF_SCRUMS,
        ScaleLevel.PROGRAM,
        ["team-ui", "team-api"],
        "daily_9am"
    )
    
    scrum_scale.schedule_ceremony(
        CeremonyType.SCALED_PLANNING,
        ScaleLevel.PORTFOLIO,
        ["program-frontend", "program-backend"],
        "quarterly"
    )
    
    logger.info(f"🏗️ Bootstrapped Scrum at Scale organization: {org_name}")
    return scrum_scale