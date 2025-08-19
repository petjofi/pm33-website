#!/usr/bin/env python3
"""
PM33 Daily Task Agent
Generates daily task lists, tracks progress, and manages weekly objectives.
Designed for flexible work schedule (5+ days/week, can work 2-3 days ahead).
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse
from pathlib import Path

class PM33DailyAgent:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.actions_dir = self.project_root / "actions"
        self.actions_dir.mkdir(exist_ok=True)
        
        # Task management files
        self.current_tasks_file = self.actions_dir / "current-tasks.json"
        self.progress_log_file = self.actions_dir / "progress-log.json"
        self.weekly_tracker_file = self.actions_dir / "weekly-tracker.json"
        
        # Initialize data structures
        self.current_tasks = self.load_current_tasks()
        self.progress_log = self.load_progress_log()
        self.weekly_tracker = self.load_weekly_tracker()
        
    def load_current_tasks(self) -> Dict:
        """Load current tasks from file or initialize empty structure."""
        if self.current_tasks_file.exists():
            with open(self.current_tasks_file, 'r') as f:
                return json.load(f)
        return {
            "date_generated": None,
            "week_number": 1,
            "week_dates": "Aug 18-24",
            "tasks": [],
            "completed_today": [],
            "notes": ""
        }
    
    def load_progress_log(self) -> Dict:
        """Load progress log from file or initialize empty structure."""
        if self.progress_log_file.exists():
            with open(self.progress_log_file, 'r') as f:
                return json.load(f)
        return {
            "daily_logs": [],
            "weekly_summaries": [],
            "metrics": {
                "total_tasks_completed": 0,
                "average_daily_completion": 0,
                "week_1_progress": 0
            }
        }
    
    def load_weekly_tracker(self) -> Dict:
        """Load weekly objectives and KPIs."""
        if self.weekly_tracker_file.exists():
            with open(self.weekly_tracker_file, 'r') as f:
                return json.load(f)
        
        # Week 1 objectives from execution plan - Updated with Strategic AI Co-Pilot focus
        return {
            "current_week": 1,
            "week_1": {
                "dates": "Aug 18-24",
                "status": "in_progress", 
                "target": "Strategic AI Co-Pilot MVP with executable workflows",
                "execution_commands_file": "/actions/week-1-execution-commands.md",
                "tasks": [
                    {
                        "id": "w1d1",
                        "task": "Day 1: Execute infrastructure setup and vendor signups",
                        "status": "pending",
                        "priority": "critical",
                        "commands": [
                            "brew install postgresql && createdb pm33_dev",
                            "pip install asyncpg sqlalchemy alembic fastapi uvicorn",
                            "Sign up: Railway, Resend, PostHog, Pinecone",
                            "Setup .env with all API keys"
                        ]
                    },
                    {
                        "id": "w1d2", 
                        "task": "Day 2: Build Strategic AI Chat API and frontend component",
                        "status": "pending",
                        "priority": "critical",
                        "commands": [
                            "Create strategic chat API endpoint",
                            "Build React StrategicChat component",
                            "Test end-to-end workflow generation",
                            "curl test API with competitor response query"
                        ]
                    },
                    {
                        "id": "w1d3",
                        "task": "Day 3: Marketing automation and lead generation setup",
                        "status": "pending",
                        "priority": "high",
                        "commands": [
                            "Sign up: Apollo.io, Hunter.io, ConvertKit",
                            "Procure 1,000 PM contacts at scale-up companies",
                            "Setup content generation automation",
                            "Create beta outreach email templates"
                        ]
                    },
                    {
                        "id": "w1d4",
                        "task": "Day 4: PM tool integrations and testing framework",
                        "status": "pending", 
                        "priority": "high",
                        "commands": [
                            "Setup Jira OAuth integration",
                            "Setup Linear API integration",
                            "Create Slack app for notifications",
                            "Setup Sentry error tracking",
                            "Create automated test suite"
                        ]
                    },
                    {
                        "id": "w1d5",
                        "task": "Day 5: Production deployment and beta launch",
                        "status": "pending",
                        "priority": "critical",
                        "commands": [
                            "Deploy to Vercel (frontend) and Railway (backend)",
                            "Purchase and configure pm33.ai domain",
                            "Launch ProductHunt campaign",
                            "Send beta outreach emails to 50 target PMs",
                            "Setup daily metrics tracking"
                        ]
                    }
                ],
                "kpis": {
                    "strategic_ai_chat": {"target": "Working end-to-end", "current": "Not started"},
                    "beta_signups": {"target": "50 users", "current": "0"},
                    "workflows_generated": {"target": "100+ workflows", "current": "0"},
                    "vendor_integrations": {"target": "5 tools connected", "current": "0"},
                    "monthly_investment": {"target": "<$150/month", "current": "$0"}
                }
            }
        }
    
    def generate_daily_tasks(self, work_ahead_days: int = 0) -> List[Dict]:
        """
        Generate daily tasks based on current week objectives and progress.
        
        Args:
            work_ahead_days: Number of days to work ahead (0 = today, 1 = tomorrow, etc.)
        """
        current_date = datetime.now() + timedelta(days=work_ahead_days)
        day_of_week = current_date.strftime("%A")
        formatted_date = current_date.strftime("%Y-%m-%d")
        
        # Get current week data
        current_week = self.weekly_tracker.get("current_week", 1)
        week_data = self.weekly_tracker.get(f"week_{current_week}", {})
        
        # Get pending tasks from current week
        pending_tasks = [task for task in week_data.get("tasks", []) 
                        if task.get("status") == "pending"]
        
        # Generate daily task recommendations based on day of week and priorities
        daily_tasks = []
        
        if day_of_week == "Monday":
            daily_tasks.extend(self._get_monday_tasks(pending_tasks))
        elif day_of_week == "Tuesday":
            daily_tasks.extend(self._get_tuesday_tasks(pending_tasks))
        elif day_of_week == "Wednesday": 
            daily_tasks.extend(self._get_wednesday_tasks(pending_tasks))
        elif day_of_week == "Thursday":
            daily_tasks.extend(self._get_thursday_tasks(pending_tasks))
        elif day_of_week == "Friday":
            daily_tasks.extend(self._get_friday_tasks(pending_tasks))
        elif day_of_week == "Saturday":
            daily_tasks.extend(self._get_weekend_tasks(pending_tasks, "saturday"))
        else:  # Sunday
            daily_tasks.extend(self._get_weekend_tasks(pending_tasks, "sunday"))
        
        # Add daily maintenance tasks
        daily_tasks.extend(self._get_daily_maintenance_tasks(current_week))
        
        return daily_tasks
    
    def _get_monday_tasks(self, pending_tasks: List[Dict]) -> List[Dict]:
        """Monday: Execute Day 1 commands - Infrastructure setup."""
        tasks = []
        
        # Check if Day 1 task exists
        day_1_task = next((task for task in pending_tasks if task.get("id") == "w1d1"), None)
        
        if day_1_task:
            # Add specific Day 1 execution commands
            tasks.extend([
                {
                    "type": "infrastructure",
                    "task": "Setup PostgreSQL database",
                    "id": "w1d1-db",
                    "priority": "critical",
                    "estimated_time": "30 minutes",
                    "commands": ["brew install postgresql", "createdb pm33_dev"]
                },
                {
                    "type": "infrastructure", 
                    "task": "Install Python dependencies",
                    "id": "w1d1-deps",
                    "priority": "critical",
                    "estimated_time": "15 minutes",
                    "commands": ["pip install asyncpg sqlalchemy alembic fastapi uvicorn python-multipart"]
                },
                {
                    "type": "vendor-signup",
                    "task": "Sign up for core services (Railway, Resend, PostHog, Pinecone)",
                    "id": "w1d1-vendors",
                    "priority": "critical",
                    "estimated_time": "1 hour",
                    "commands": ["Visit signup URLs from execution-commands.md", "Configure API keys in .env"]
                },
                {
                    "type": "development",
                    "task": "Initialize strategic workflow backend",
                    "id": "w1d1-backend",
                    "priority": "high",
                    "estimated_time": "2 hours",
                    "commands": ["alembic init alembic", "alembic revision --autogenerate", "python strategic-workflow-engine.py"]
                }
            ])
        else:
            # Fallback to general Monday tasks
            tasks.append({
                "type": "planning",
                "task": "Review week objectives and execution plan",
                "priority": "high",
                "estimated_time": "30 minutes"
            })
        
        return tasks
    
    def _get_tuesday_tasks(self, pending_tasks: List[Dict]) -> List[Dict]:
        """Tuesday: Execute Day 2 commands - Strategic AI Chat implementation."""
        tasks = []
        
        # Check if Day 2 task exists
        day_2_task = next((task for task in pending_tasks if task.get("id") == "w1d2"), None)
        
        if day_2_task:
            tasks.extend([
                {
                    "type": "api-development",
                    "task": "Create Strategic AI Chat API endpoint",
                    "id": "w1d2-api",
                    "priority": "critical",
                    "estimated_time": "2 hours",
                    "commands": ["Create strategic_chat.py route", "Test with curl command"]
                },
                {
                    "type": "frontend-development",
                    "task": "Build StrategicChat React component",
                    "id": "w1d2-frontend", 
                    "priority": "critical",
                    "estimated_time": "2 hours",
                    "commands": ["Create StrategicChat.tsx", "npm install dependencies", "npm run dev"]
                },
                {
                    "type": "integration-testing",
                    "task": "Test end-to-end strategic workflow generation",
                    "id": "w1d2-testing",
                    "priority": "high",
                    "estimated_time": "1 hour",
                    "commands": ["Test competitor response query", "Verify workflow creation", "Check task generation"]
                }
            ])
        else:
            # Fallback to continuing previous day's work
            tasks.append({
                "type": "development",
                "task": "Continue Strategic AI implementation",
                "priority": "high",
                "estimated_time": "3 hours"
            })
        
        return tasks
    
    def _get_wednesday_tasks(self, pending_tasks: List[Dict]) -> List[Dict]:
        """Wednesday: Mid-week progress review and medium priority tasks."""
        tasks = []
        
        # Mid-week review
        tasks.append({
            "type": "review",
            "task": "Mid-week progress review and task adjustment",
            "priority": "medium",
            "estimated_time": "20 minutes"
        })
        
        # Work on medium priority tasks
        medium_priority = [task for task in pending_tasks 
                          if task.get("priority") == "medium"][:2]
        
        for task in medium_priority:
            tasks.append({
                "type": "development",
                "task": task.get("task"),
                "id": task.get("id"),
                "priority": "medium",
                "estimated_time": "1-2 hours"
            })
        
        return tasks
    
    def _get_thursday_tasks(self, pending_tasks: List[Dict]) -> List[Dict]:
        """Thursday: Complete remaining high-priority tasks."""
        tasks = []
        
        # Focus on completing remaining high-priority items
        remaining_high = [task for task in pending_tasks 
                         if task.get("priority") == "high"]
        
        for task in remaining_high[:2]:
            tasks.append({
                "type": "development", 
                "task": task.get("task"),
                "id": task.get("id"),
                "priority": "high",
                "estimated_time": "2-3 hours"
            })
        
        # Add monitoring setup if still pending
        monitoring_task = next((task for task in pending_tasks 
                               if "monitoring" in task.get("task", "").lower()), None)
        if monitoring_task:
            tasks.append({
                "type": "monitoring",
                "task": "Deploy initial monitoring setup",
                "id": monitoring_task.get("id"),
                "priority": "medium",
                "estimated_time": "1-2 hours"
            })
        
        return tasks
    
    def _get_friday_tasks(self, pending_tasks: List[Dict]) -> List[Dict]:
        """Friday: Week completion and next week preparation."""
        tasks = []
        
        # Complete any remaining tasks
        remaining_tasks = pending_tasks[:2]
        for task in remaining_tasks:
            tasks.append({
                "type": "completion",
                "task": task.get("task"),
                "id": task.get("id"), 
                "priority": task.get("priority", "medium"),
                "estimated_time": "1-2 hours"
            })
        
        # Week wrap-up
        tasks.append({
            "type": "planning",
            "task": "Week 1 completion review and Week 2 preparation",
            "priority": "high",
            "estimated_time": "45 minutes"
        })
        
        return tasks
    
    def _get_weekend_tasks(self, pending_tasks: List[Dict], day: str) -> List[Dict]:
        """Weekend: Lighter tasks and strategic thinking."""
        tasks = []
        
        if day == "saturday":
            # Strategic tasks on Saturday
            tasks.append({
                "type": "strategic",
                "task": "Review market research findings and adjust strategy",
                "priority": "medium",
                "estimated_time": "1 hour"
            })
            
            # Light development work
            easy_tasks = [task for task in pending_tasks 
                         if task.get("priority") == "medium"][:1]
            for task in easy_tasks:
                tasks.append({
                    "type": "development",
                    "task": task.get("task"),
                    "id": task.get("id"),
                    "priority": "medium",
                    "estimated_time": "1-2 hours"
                })
        
        else:  # Sunday
            # Planning and preparation
            tasks.append({
                "type": "planning", 
                "task": "Next week planning and objective setting",
                "priority": "medium",
                "estimated_time": "30 minutes"
            })
        
        return tasks
    
    def _get_daily_maintenance_tasks(self, current_week: int) -> List[Dict]:
        """Daily maintenance tasks that should be done regardless of day."""
        tasks = []
        
        # Always include these
        tasks.extend([
            {
                "type": "maintenance",
                "task": "Check and respond to critical communications",
                "priority": "high", 
                "estimated_time": "15 minutes"
            },
            {
                "type": "maintenance",
                "task": "Update task progress and log work completed",
                "priority": "medium",
                "estimated_time": "10 minutes"
            }
        ])
        
        # Week-specific maintenance
        if current_week == 1:
            tasks.append({
                "type": "maintenance",
                "task": "Monitor Claude Code automation setup",
                "priority": "medium",
                "estimated_time": "10 minutes"
            })
        
        return tasks
    
    def mark_task_complete(self, task_id: str, notes: str = ""):
        """Mark a specific task as complete."""
        current_week = self.weekly_tracker.get("current_week", 1)
        week_data = self.weekly_tracker.get(f"week_{current_week}", {})
        
        # Update task status in weekly tracker
        for task in week_data.get("tasks", []):
            if task.get("id") == task_id:
                task["status"] = "completed"
                task["completed_date"] = datetime.now().isoformat()
                if notes:
                    task["completion_notes"] = notes
                break
        
        # Log completion
        today = datetime.now().strftime("%Y-%m-%d")
        completion_entry = {
            "date": today,
            "task_id": task_id,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.current_tasks["completed_today"].append(completion_entry)
        self.progress_log["metrics"]["total_tasks_completed"] += 1
        
        self.save_all_data()
        print(f"✅ Task {task_id} marked as complete!")
    
    def add_progress_note(self, note: str):
        """Add a progress note for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        progress_entry = {
            "date": today,
            "note": note,
            "timestamp": datetime.now().isoformat()
        }
        
        self.progress_log["daily_logs"].append(progress_entry)
        self.save_all_data()
        print(f"📝 Progress note added: {note}")
    
    def generate_daily_output(self, work_ahead_days: int = 0) -> str:
        """Generate formatted daily task list output."""
        target_date = datetime.now() + timedelta(days=work_ahead_days)
        formatted_date = target_date.strftime("%A, %B %d, %Y")
        
        daily_tasks = self.generate_daily_tasks(work_ahead_days)
        
        # Update current tasks
        self.current_tasks.update({
            "date_generated": target_date.isoformat(),
            "tasks": daily_tasks,
            "completed_today": [],
            "notes": ""
        })
        
        output = [
            f"# PM33 Daily Tasks - {formatted_date}",
            f"",
            f"## Week {self.weekly_tracker.get('current_week', 1)} Progress Status",
            f"Target: {self.weekly_tracker.get('week_1', {}).get('target', 'Complete unified workspace and automation foundation')}",
            f"",
            f"## Today's Tasks ({len(daily_tasks)} items)",
            f""
        ]
        
        # Group tasks by type
        task_types = {}
        for task in daily_tasks:
            task_type = task.get("type", "general")
            if task_type not in task_types:
                task_types[task_type] = []
            task_types[task_type].append(task)
        
        # Output tasks by type
        type_order = ["planning", "development", "automation", "monitoring", "strategic", "completion", "review", "maintenance"]
        
        for task_type in type_order:
            if task_type in task_types:
                output.append(f"### {task_type.title()} Tasks")
                for i, task in enumerate(task_types[task_type], 1):
                    priority_emoji = "🔴" if task.get("priority") == "high" else "🟡" if task.get("priority") == "medium" else "🟢"
                    task_id = task.get("id", f"daily-{task_type}-{i}")
                    estimated_time = task.get("estimated_time", "30 minutes")
                    
                    output.append(f"- [ ] **{task.get('task')}** {priority_emoji}")
                    output.append(f"  - ID: `{task_id}`")
                    output.append(f"  - Estimated Time: {estimated_time}")
                    output.append("")
        
        # Add quick commands section
        output.extend([
            "## Quick Commands",
            "```bash",
            "# Mark task complete:",
            "python actions/daily-agent.py complete <task_id> --notes 'completion notes'",
            "",
            "# Add progress note:",
            "python actions/daily-agent.py note 'your progress note'", 
            "",
            "# Generate tomorrow's tasks:",
            "python actions/daily-agent.py generate --days-ahead 1",
            "",
            "# View week status:",
            "python actions/daily-agent.py status",
            "```",
            ""
        ])
        
        # Add current week status
        current_week = self.weekly_tracker.get("current_week", 1)
        week_data = self.weekly_tracker.get(f"week_{current_week}", {})
        total_tasks = len(week_data.get("tasks", []))
        completed_tasks = len([t for t in week_data.get("tasks", []) if t.get("status") == "completed"])
        
        output.extend([
            f"## Week {current_week} Status",
            f"- Progress: {completed_tasks}/{total_tasks} tasks completed ({int(completed_tasks/total_tasks*100) if total_tasks > 0 else 0}%)",
            f"- Remaining: {total_tasks - completed_tasks} tasks",
            ""
        ])
        
        self.save_all_data()
        return "\n".join(output)
    
    def get_week_status(self) -> str:
        """Generate week status report."""
        current_week = self.weekly_tracker.get("current_week", 1)
        week_data = self.weekly_tracker.get(f"week_{current_week}", {})
        
        output = [
            f"# Week {current_week} Status Report",
            f"**Dates**: {week_data.get('dates', 'N/A')}",
            f"**Target**: {week_data.get('target', 'N/A')}",
            f"**Status**: {week_data.get('status', 'unknown')}",
            f"",
            f"## Task Progress"
        ]
        
        for task in week_data.get("tasks", []):
            status_emoji = "✅" if task.get("status") == "completed" else "⏳" if task.get("status") == "in_progress" else "⭕"
            priority_emoji = "🔴" if task.get("priority") == "high" else "🟡" if task.get("priority") == "medium" else "🟢"
            
            output.append(f"- {status_emoji} **{task.get('task')}** {priority_emoji}")
            if task.get("status") == "completed" and task.get("completed_date"):
                output.append(f"  - Completed: {task.get('completed_date')[:10]}")
            output.append("")
        
        # KPI Status
        output.extend([
            "## KPI Progress",
            ""
        ])
        
        for kpi_name, kpi_data in week_data.get("kpis", {}).items():
            target = kpi_data.get("target", "N/A")
            current = kpi_data.get("current", "N/A") 
            output.append(f"- **{kpi_name.replace('_', ' ').title()}**: {current} (Target: {target})")
        
        return "\n".join(output)
    
    def save_all_data(self):
        """Save all data structures to files."""
        with open(self.current_tasks_file, 'w') as f:
            json.dump(self.current_tasks, f, indent=2)
        
        with open(self.progress_log_file, 'w') as f:
            json.dump(self.progress_log, f, indent=2)
        
        with open(self.weekly_tracker_file, 'w') as f:
            json.dump(self.weekly_tracker, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="PM33 Daily Task Agent")
    parser.add_argument("command", choices=["generate", "complete", "note", "status"], 
                       help="Command to execute")
    parser.add_argument("--days-ahead", type=int, default=0,
                       help="Days ahead to generate tasks for (0 = today)")
    parser.add_argument("task_id", nargs="?", help="Task ID for completion")
    parser.add_argument("--notes", help="Notes for task completion")
    parser.add_argument("note_text", nargs="?", help="Progress note text")
    
    args = parser.parse_args()
    
    # Get project root (assuming script is in actions/ subdirectory)
    project_root = Path(__file__).parent.parent
    agent = PM33DailyAgent(str(project_root))
    
    if args.command == "generate":
        output = agent.generate_daily_output(args.days_ahead)
        print(output)
        
        # Save to dated file
        target_date = datetime.now() + timedelta(days=args.days_ahead)
        filename = f"daily-tasks-{target_date.strftime('%Y-%m-%d')}.md"
        output_file = agent.actions_dir / filename
        
        with open(output_file, 'w') as f:
            f.write(output)
        
        print(f"\n📄 Tasks saved to: {output_file}")
        
    elif args.command == "complete":
        if not args.task_id:
            print("❌ Task ID required for completion")
            return
        agent.mark_task_complete(args.task_id, args.notes or "")
        
    elif args.command == "note":
        if not args.note_text:
            print("❌ Note text required")
            return
        agent.add_progress_note(args.note_text)
        
    elif args.command == "status":
        status = agent.get_week_status()
        print(status)

if __name__ == "__main__":
    main()