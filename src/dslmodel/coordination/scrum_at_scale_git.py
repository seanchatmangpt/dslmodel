"""
Scrum at Scale Git Coordination System
Federated agile coordination using Git as the substrate
"""

import subprocess
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from opentelemetry import trace

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
tracer = trace.get_tracer(__name__)

class SprintStatus(Enum):
    """Sprint status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    REVIEW = "review"
    RETROSPECTIVE = "retrospective"
    COMPLETED = "completed"

class TeamRole(Enum):
    """Team member roles"""
    SCRUM_MASTER = "scrum_master"
    PRODUCT_OWNER = "product_owner"
    DEVELOPER = "developer"
    ARCHITECT = "architect"
    QA_ENGINEER = "qa_engineer"

class DependencyType(Enum):
    """Types of inter-team dependencies"""
    API_CONTRACT = "api_contract"
    SHARED_COMPONENT = "shared_component"
    DATA_SCHEMA = "data_schema"
    INFRASTRUCTURE = "infrastructure"
    DOMAIN_KNOWLEDGE = "domain_knowledge"

@dataclass
class TeamMember:
    """Individual team member"""
    name: str
    email: str
    role: TeamRole
    git_username: str
    capacity: float = 1.0  # 0.0 to 1.0
    specializations: List[str] = field(default_factory=list)

@dataclass
class ScrumTeam:
    """Individual Scrum team"""
    id: str
    name: str
    domain: str  # Business domain
    members: List[TeamMember]
    git_remote: str
    worktree_path: str
    current_sprint: Optional[str] = None
    velocity: float = 0.0
    capacity: float = 0.0
    
    def __post_init__(self):
        """Calculate team capacity"""
        self.capacity = sum(member.capacity for member in self.members)

@dataclass
class UserStory:
    """User story / backlog item"""
    id: str
    title: str
    description: str
    story_points: int
    team_id: str
    sprint_id: Optional[str] = None
    status: str = "todo"  # todo, in_progress, done
    dependencies: List[str] = field(default_factory=list)
    git_branch: Optional[str] = None
    
@dataclass
class Dependency:
    """Inter-team dependency"""
    id: str
    type: DependencyType
    source_team: str
    target_team: str
    description: str
    due_date: datetime
    status: str = "pending"  # pending, in_progress, resolved, blocked
    git_refs: List[str] = field(default_factory=list)

@dataclass
class Sprint:
    """Sprint configuration"""
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    teams: List[str]  # Team IDs
    goals: List[str]
    status: SprintStatus
    stories: List[str] = field(default_factory=list)  # Story IDs
    dependencies: List[str] = field(default_factory=list)  # Dependency IDs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git storage"""
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "teams": self.teams,
            "goals": self.goals,
            "status": self.status.value,
            "stories": self.stories,
            "dependencies": self.dependencies
        }

@dataclass
class ProgramIncrement:
    """Program Increment (PI) for Scrum at Scale"""
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    sprints: List[str]  # Sprint IDs
    objectives: List[str]
    teams: List[str]  # All participating team IDs
    dependencies: List[str]  # Cross-PI dependencies
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git storage"""
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "sprints": self.sprints,
            "objectives": self.objectives,
            "teams": self.teams,
            "dependencies": self.dependencies
        }

class GitFederationManager:
    """Manages Git federation for Scrum at Scale"""
    
    def __init__(self):
        self.worktree_base = Path("scrum_worktrees")
        self.domain_packs_base = Path("domain_packs")
        
    def setup_team_worktree(self, team: ScrumTeam, sprint_id: str) -> bool:
        """Create isolated worktree for team sprint work"""
        
        try:
            worktree_path = self.worktree_base / f"{team.id}_{sprint_id}"
            
            # Create worktree for team's sprint work
            result = subprocess.run([
                "git", "worktree", "add", 
                str(worktree_path), f"sprint/{sprint_id}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                # Create branch if it doesn't exist
                subprocess.run([
                    "git", "checkout", "-b", f"sprint/{sprint_id}"
                ], capture_output=True, text=True)
                
                # Try worktree again
                result = subprocess.run([
                    "git", "worktree", "add", 
                    str(worktree_path), f"sprint/{sprint_id}"
                ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print(f"🏗️ Created worktree for {team.name}: {worktree_path}")
                team.worktree_path = str(worktree_path)
                return True
            else:
                console.print(f"❌ Failed to create worktree: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error setting up worktree: {e}")
            return False
    
    def setup_domain_pack(self, team: ScrumTeam) -> bool:
        """Add team's domain pack as submodule"""
        
        try:
            if team.git_remote:
                domain_path = self.domain_packs_base / team.domain
                
                # Add domain pack as submodule
                result = subprocess.run([
                    "git", "submodule", "add", 
                    team.git_remote, str(domain_path)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    console.print(f"📦 Added domain pack for {team.name}: {domain_path}")
                    return True
                else:
                    # Might already exist
                    if "already exists" in result.stderr:
                        console.print(f"📦 Domain pack already exists for {team.name}")
                        return True
                    else:
                        console.print(f"❌ Failed to add domain pack: {result.stderr}")
                        return False
            else:
                console.print(f"⚠️ No Git remote configured for {team.name}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error setting up domain pack: {e}")
            return False
    
    def sync_federation(self, teams: List[ScrumTeam]) -> Dict[str, Any]:
        """Sync all federated repositories"""
        
        sync_results = {}
        
        with tracer.start_as_current_span("scrum.federation.sync") as span:
            
            # Fetch all remotes
            result = subprocess.run([
                "git", "fetch", "--all"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("🔄 Fetched all federation remotes")
                sync_results["fetch_success"] = True
            else:
                console.print(f"⚠️ Federation fetch warnings: {result.stderr}")
                sync_results["fetch_success"] = False
            
            # Update submodules
            result = subprocess.run([
                "git", "submodule", "update", "--remote"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("📦 Updated domain pack submodules")
                sync_results["submodule_success"] = True
            else:
                console.print(f"⚠️ Submodule update issues: {result.stderr}")
                sync_results["submodule_success"] = False
            
            # Get federation status
            federation_status = self.get_federation_status()
            sync_results.update(federation_status)
            
            span.set_attribute("sync.teams", len(teams))
            span.set_attribute("sync.fetch_success", sync_results["fetch_success"])
            span.set_attribute("sync.submodule_success", sync_results["submodule_success"])
            
        return sync_results
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get current federation status"""
        
        try:
            # Get remote status
            result = subprocess.run([
                "git", "remote", "-v"
            ], capture_output=True, text=True)
            
            remotes = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip() and "(fetch)" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            remotes.append(parts[0])
            
            # Get submodule status
            result = subprocess.run([
                "git", "submodule", "status"
            ], capture_output=True, text=True)
            
            submodules = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            submodules.append(parts[1])
            
            # Get worktree status
            result = subprocess.run([
                "git", "worktree", "list"
            ], capture_output=True, text=True)
            
            worktrees = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            worktrees.append(parts[0])
            
            return {
                "remotes": remotes,
                "submodules": submodules,
                "worktrees": worktrees,
                "federation_health": len(remotes) > 0 and len(submodules) > 0
            }
            
        except Exception as e:
            console.print(f"❌ Error getting federation status: {e}")
            return {
                "remotes": [],
                "submodules": [],
                "worktrees": [],
                "federation_health": False
            }

class ScrumAtScaleCoordinator:
    """Main Scrum at Scale coordination system"""
    
    def __init__(self):
        self.federation = GitFederationManager()
        self.teams: Dict[str, ScrumTeam] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.program_increments: Dict[str, ProgramIncrement] = {}
        self.dependencies: Dict[str, Dependency] = {}
        self.stories: Dict[str, UserStory] = {}
        
        self.notes_ref_sprints = "refs/notes/scrum/sprints"
        self.notes_ref_teams = "refs/notes/scrum/teams"
        self.notes_ref_pi = "refs/notes/scrum/program-increments"
        
        console.print("🏃‍♂️ Scrum at Scale Git Coordinator initialized")
    
    def register_team(self, team_id: str, name: str, domain: str, 
                     members: List[Dict[str, Any]], git_remote: str = "") -> ScrumTeam:
        """Register a new Scrum team"""
        
        team_members = [
            TeamMember(
                name=m["name"],
                email=m["email"],
                role=TeamRole(m["role"]),
                git_username=m["git_username"],
                capacity=m.get("capacity", 1.0),
                specializations=m.get("specializations", [])
            )
            for m in members
        ]
        
        team = ScrumTeam(
            id=team_id,
            name=name,
            domain=domain,
            members=team_members,
            git_remote=git_remote,
            worktree_path=""
        )
        
        self.teams[team_id] = team
        
        # Setup Git federation for team
        if git_remote:
            self.federation.setup_domain_pack(team)
        
        console.print(f"👥 Registered team: {name} ({domain} domain)")
        return team
    
    def create_sprint(self, sprint_id: str, name: str, duration_weeks: int = 2,
                     team_ids: List[str] = None, goals: List[str] = None) -> Sprint:
        """Create a new sprint"""
        
        if team_ids is None:
            team_ids = list(self.teams.keys())
        
        if goals is None:
            goals = []
        
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        sprint = Sprint(
            id=sprint_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            teams=team_ids,
            goals=goals,
            status=SprintStatus.PLANNING
        )
        
        self.sprints[sprint_id] = sprint
        
        # Setup worktrees for participating teams
        for team_id in team_ids:
            if team_id in self.teams:
                team = self.teams[team_id]
                self.federation.setup_team_worktree(team, sprint_id)
                team.current_sprint = sprint_id
        
        # Store in Git notes
        self.store_sprint_in_git(sprint)
        
        console.print(f"🏃‍♂️ Created sprint: {name} ({duration_weeks} weeks)")
        return sprint
    
    def create_program_increment(self, pi_id: str, name: str, duration_weeks: int = 10,
                               objectives: List[str] = None) -> ProgramIncrement:
        """Create a Program Increment for large-scale coordination"""
        
        if objectives is None:
            objectives = []
        
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        # Create sprints for the PI (typically 5 sprints of 2 weeks each)
        sprint_ids = []
        for i in range(5):
            sprint_start = start_date + timedelta(weeks=i*2)
            sprint_end = sprint_start + timedelta(weeks=2)
            
            sprint_id = f"{pi_id}_sprint_{i+1}"
            sprint_name = f"{name} Sprint {i+1}"
            
            sprint = Sprint(
                id=sprint_id,
                name=sprint_name,
                start_date=sprint_start,
                end_date=sprint_end,
                teams=list(self.teams.keys()),
                goals=[f"PI objective delivery for sprint {i+1}"],
                status=SprintStatus.PLANNING if i == 0 else SprintStatus.PLANNING
            )
            
            self.sprints[sprint_id] = sprint
            sprint_ids.append(sprint_id)
        
        pi = ProgramIncrement(
            id=pi_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            sprints=sprint_ids,
            objectives=objectives,
            teams=list(self.teams.keys()),
            dependencies=[]
        )
        
        self.program_increments[pi_id] = pi
        
        # Store in Git notes
        self.store_pi_in_git(pi)
        
        console.print(f"📅 Created Program Increment: {name} ({duration_weeks} weeks, {len(sprint_ids)} sprints)")
        return pi
    
    def add_dependency(self, source_team: str, target_team: str, 
                      dependency_type: DependencyType, description: str,
                      due_date: datetime = None) -> Dependency:
        """Add inter-team dependency"""
        
        if due_date is None:
            due_date = datetime.now(timezone.utc) + timedelta(weeks=2)
        
        dep_id = str(uuid.uuid4())[:8]
        
        dependency = Dependency(
            id=dep_id,
            type=dependency_type,
            source_team=source_team,
            target_team=target_team,
            description=description,
            due_date=due_date
        )
        
        self.dependencies[dep_id] = dependency
        
        console.print(f"🔗 Added dependency: {source_team} → {target_team} ({dependency_type.value})")
        return dependency
    
    def daily_standup_sync(self) -> Dict[str, Any]:
        """Perform daily standup synchronization across teams"""
        
        with tracer.start_as_current_span("scrum.daily_standup") as span:
            
            console.print("🌅 Starting daily standup synchronization...")
            
            # Sync federation
            sync_results = self.federation.sync_federation(list(self.teams.values()))
            
            # Gather team progress
            team_progress = {}
            for team_id, team in self.teams.items():
                progress = self.get_team_progress(team_id)
                team_progress[team_id] = progress
            
            # Identify blockers and dependencies
            blockers = self.identify_blockers()
            
            # Generate cross-team coordination report
            coordination_report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "federation_sync": sync_results,
                "team_progress": team_progress,
                "blockers": blockers,
                "active_dependencies": len([d for d in self.dependencies.values() if d.status == "in_progress"])
            }
            
            # Store daily standup results in Git notes
            self.store_daily_standup(coordination_report)
            
            # Display summary
            self.display_daily_standup_summary(coordination_report)
            
            span.set_attribute("teams_count", len(self.teams))
            span.set_attribute("blockers_count", len(blockers))
            span.set_attribute("federation_healthy", sync_results.get("federation_health", False))
            
            return coordination_report
    
    def get_team_progress(self, team_id: str) -> Dict[str, Any]:
        """Get current progress for a team"""
        
        if team_id not in self.teams:
            return {}
        
        team = self.teams[team_id]
        
        # Get team's stories for current sprint
        team_stories = [s for s in self.stories.values() 
                       if s.team_id == team_id and s.sprint_id == team.current_sprint]
        
        total_points = sum(s.story_points for s in team_stories)
        completed_points = sum(s.story_points for s in team_stories if s.status == "done")
        
        progress_percentage = (completed_points / total_points * 100) if total_points > 0 else 0
        
        return {
            "team_name": team.name,
            "current_sprint": team.current_sprint,
            "total_stories": len(team_stories),
            "completed_stories": len([s for s in team_stories if s.status == "done"]),
            "total_points": total_points,
            "completed_points": completed_points,
            "progress_percentage": progress_percentage,
            "team_capacity": team.capacity,
            "velocity": team.velocity
        }
    
    def identify_blockers(self) -> List[Dict[str, Any]]:
        """Identify cross-team blockers"""
        
        blockers = []
        
        # Check overdue dependencies
        now = datetime.now(timezone.utc)
        for dep in self.dependencies.values():
            if dep.due_date < now and dep.status not in ["resolved", "cancelled"]:
                blockers.append({
                    "type": "overdue_dependency",
                    "dependency_id": dep.id,
                    "source_team": dep.source_team,
                    "target_team": dep.target_team,
                    "description": dep.description,
                    "days_overdue": (now - dep.due_date).days
                })
        
        # Check for teams with zero progress
        for team_id, team in self.teams.items():
            progress = self.get_team_progress(team_id)
            if progress.get("progress_percentage", 0) == 0 and team.current_sprint:
                blockers.append({
                    "type": "team_blocked",
                    "team_id": team_id,
                    "team_name": team.name,
                    "sprint": team.current_sprint,
                    "description": "No progress in current sprint"
                })
        
        return blockers
    
    def sprint_review_integration(self, sprint_id: str) -> Dict[str, Any]:
        """Integrate sprint deliverables"""
        
        with tracer.start_as_current_span("scrum.sprint_review") as span:
            
            if sprint_id not in self.sprints:
                console.print("❌ Sprint not found")
                return {}
            
            sprint = self.sprints[sprint_id]
            console.print(f"📋 Starting sprint review integration for: {sprint.name}")
            
            integration_results = {
                "sprint_id": sprint_id,
                "teams": [],
                "integration_success": True,
                "merged_branches": [],
                "failed_merges": []
            }
            
            # Cherry-pick completed features from team worktrees
            for team_id in sprint.teams:
                if team_id in self.teams:
                    team = self.teams[team_id]
                    team_result = self.integrate_team_deliverables(team, sprint_id)
                    integration_results["teams"].append(team_result)
                    
                    if not team_result.get("success", False):
                        integration_results["integration_success"] = False
            
            # Update sprint status
            if integration_results["integration_success"]:
                sprint.status = SprintStatus.COMPLETED
                console.print(f"✅ Sprint {sprint.name} integration completed successfully")
            else:
                sprint.status = SprintStatus.REVIEW
                console.print(f"⚠️ Sprint {sprint.name} integration had issues")
            
            # Store integration results
            self.store_sprint_in_git(sprint)
            
            span.set_attribute("sprint.teams", len(sprint.teams))
            span.set_attribute("integration.success", integration_results["integration_success"])
            
            return integration_results
    
    def integrate_team_deliverables(self, team: ScrumTeam, sprint_id: str) -> Dict[str, Any]:
        """Integrate deliverables from a team's worktree"""
        
        try:
            # Get team's completed stories
            team_stories = [s for s in self.stories.values() 
                          if s.team_id == team.id and s.sprint_id == sprint_id and s.status == "done"]
            
            merged_branches = []
            failed_merges = []
            
            for story in team_stories:
                if story.git_branch:
                    # Try to cherry-pick the story's commits
                    result = subprocess.run([
                        "git", "cherry-pick", f"origin/{story.git_branch}"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        merged_branches.append(story.git_branch)
                        console.print(f"🍒 Cherry-picked: {story.git_branch}")
                    else:
                        failed_merges.append({
                            "branch": story.git_branch,
                            "error": result.stderr
                        })
                        console.print(f"❌ Failed to cherry-pick: {story.git_branch}")
            
            return {
                "team_id": team.id,
                "team_name": team.name,
                "success": len(failed_merges) == 0,
                "completed_stories": len(team_stories),
                "merged_branches": merged_branches,
                "failed_merges": failed_merges
            }
            
        except Exception as e:
            console.print(f"❌ Error integrating {team.name} deliverables: {e}")
            return {
                "team_id": team.id,
                "team_name": team.name,
                "success": False,
                "error": str(e)
            }
    
    def store_sprint_in_git(self, sprint: Sprint):
        """Store sprint data in Git notes"""
        try:
            sprint_json = json.dumps(sprint.to_dict(), indent=2)
            subprocess.run([
                "git", "notes", "--ref", self.notes_ref_sprints,
                "add", "-m", sprint_json, "HEAD"
            ], capture_output=True, text=True)
        except Exception as e:
            console.print(f"⚠️ Could not store sprint in Git: {e}")
    
    def store_pi_in_git(self, pi: ProgramIncrement):
        """Store Program Increment data in Git notes"""
        try:
            pi_json = json.dumps(pi.to_dict(), indent=2)
            subprocess.run([
                "git", "notes", "--ref", self.notes_ref_pi,
                "add", "-m", pi_json, "HEAD"
            ], capture_output=True, text=True)
        except Exception as e:
            console.print(f"⚠️ Could not store PI in Git: {e}")
    
    def store_daily_standup(self, report: Dict[str, Any]):
        """Store daily standup report in Git notes"""
        try:
            report_json = json.dumps(report, indent=2)
            subprocess.run([
                "git", "notes", "--ref", "refs/notes/scrum/daily-standups",
                "append", "-m", report_json, "HEAD"
            ], capture_output=True, text=True)
        except Exception as e:
            console.print(f"⚠️ Could not store daily standup: {e}")
    
    def display_daily_standup_summary(self, report: Dict[str, Any]):
        """Display daily standup summary"""
        
        table = Table(title="Daily Scrum at Scale Summary")
        table.add_column("Team", style="cyan")
        table.add_column("Progress", style="white")
        table.add_column("Stories", style="green")
        table.add_column("Points", style="blue")
        table.add_column("Velocity", style="yellow")
        
        for team_id, progress in report["team_progress"].items():
            team_name = progress.get("team_name", team_id)
            progress_pct = progress.get("progress_percentage", 0)
            completed_stories = progress.get("completed_stories", 0)
            total_stories = progress.get("total_stories", 0)
            completed_points = progress.get("completed_points", 0)
            total_points = progress.get("total_points", 0)
            velocity = progress.get("velocity", 0)
            
            table.add_row(
                team_name,
                f"{progress_pct:.1f}%",
                f"{completed_stories}/{total_stories}",
                f"{completed_points}/{total_points}",
                f"{velocity:.1f}"
            )
        
        console.print(table)
        
        # Blockers summary
        if report["blockers"]:
            console.print("\n🚫 Active Blockers:")
            for blocker in report["blockers"]:
                console.print(f"  • {blocker['type']}: {blocker.get('description', 'No description')}")
        else:
            console.print("\n✅ No active blockers detected")
        
        # Federation status
        federation_health = report["federation_sync"].get("federation_health", False)
        federation_status = "🟢 HEALTHY" if federation_health else "🔴 DEGRADED"
        console.print(f"\n🔗 Federation Status: {federation_status}")


# CLI interface for testing
if __name__ == "__main__":
    import typer
    
    app = typer.Typer(name="scrum-git", help="Scrum at Scale Git coordination")
    
    coordinator = ScrumAtScaleCoordinator()
    
    @app.command()
    def register_team(team_id: str, name: str, domain: str):
        """Register a new Scrum team"""
        # Mock team members for demo
        members = [
            {
                "name": f"{name} Developer 1",
                "email": f"dev1@{domain}.com",
                "role": "developer",
                "git_username": f"dev1_{team_id}",
                "capacity": 1.0
            },
            {
                "name": f"{name} Scrum Master",
                "email": f"sm@{domain}.com", 
                "role": "scrum_master",
                "git_username": f"sm_{team_id}",
                "capacity": 0.8
            }
        ]
        
        team = coordinator.register_team(team_id, name, domain, members)
        console.print(f"Team registered: {team.name}")
    
    @app.command()
    def create_sprint(sprint_id: str, name: str, weeks: int = 2):
        """Create a new sprint"""
        sprint = coordinator.create_sprint(sprint_id, name, weeks)
        console.print(f"Sprint created: {sprint.name}")
    
    @app.command()
    def create_pi(pi_id: str, name: str, weeks: int = 10):
        """Create a Program Increment"""
        pi = coordinator.create_program_increment(pi_id, name, weeks)
        console.print(f"Program Increment created: {pi.name}")
    
    @app.command()
    def daily_standup():
        """Run daily standup synchronization"""
        coordinator.daily_standup_sync()
    
    @app.command()
    def sprint_review(sprint_id: str):
        """Run sprint review integration"""
        results = coordinator.sprint_review_integration(sprint_id)
        console.print(f"Sprint review completed for: {sprint_id}")
    
    app()