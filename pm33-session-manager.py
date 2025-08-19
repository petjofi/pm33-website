#!/usr/bin/env python3
"""
PM33 Unified Session Manager
Combines session startup and shutdown into one comprehensive tool

⚠️ IMPORTANT: Keep this file updated whenever project evolves!
- Update PROJECT_OVERVIEW when vision/goals change
- Update STRATEGIC_PRIORITIES when phases shift  
- Update DOCUMENT_REFERENCES when new files are created
- Update SUCCESS_METRICS when targets change

Last Updated: 2025-08-18 (PMO transformation vision + unified session management)
"""

import os
import sys
import subprocess
from datetime import datetime

class PM33SessionManager:
    def __init__(self):
        self.project_path = "/Users/ssaper/Desktop/my-projects/pm33-claude-execution"
        self.ensure_project_directory()
        self.file_registry = self.build_file_registry()
        
    def ensure_project_directory(self):
        """Ensure we're in the correct project directory"""
        if not os.path.exists(os.path.join(os.getcwd(), "PM33_COMPLETE_CONTEXT_LOADER.py")):
            if os.path.exists(self.project_path):
                os.chdir(self.project_path)
            else:
                print("❌ Error: PM33 project directory not found!")
                sys.exit(1)
    
    def build_file_registry(self):
        """Build comprehensive registry of all key project files for agents"""
        return {
            # Core Documentation
            'instructions': 'INSTRUCTIONS-FOR-FUTURE-AGENTS.md',
            'session_checklist': 'PM33-SESSION-CHECKLIST.md',
            'session_maintenance': 'SESSION-FILES-MAINTENANCE.md',
            
            # Demo & Marketing Files
            'demo_design': 'PM33_CLICKABLE_DEMO_DESIGN.md',
            'ux_architecture': 'PM33_UX_ARCHITECTURE_PLAN.md', 
            'demo_positioning': 'DEMO-POSITIONING-GUIDE.md',
            'testing_guide': 'DEVELOPMENT-TESTING-GUIDE.md',
            'marketing_plan': 'marketing/DAY3-BETA-OUTREACH-PLAN.md',
            
            # Design System Documentation
            'design_system_guide': 'app/frontend/PM33_DESIGN_SYSTEM_GUIDE.md',
            'marketing_design_system': 'app/frontend/MARKETING_DESIGN_SYSTEM.md',
            'app_design_system': 'app/frontend/APP_DESIGN_SYSTEM.md',
            'design_implementation': 'app/frontend/design-system-implementation.md',
            
            # Strategic Planning
            'strategic_context': 'STRATEGIC-CONTEXT-REQUIREMENTS.md',
            'workflow_analysis': 'PM33_DEEP_WORKFLOW_ANALYSIS.md',
            'data_requirements': 'PM33_DATA_REQUIREMENTS_ARCHITECTURE.md',
            'information_architecture': 'PM33_INFORMATION_ARCHITECTURE_NAVIGATION.md',
            'onboarding_design': 'PM33_STRATEGIC_ONBOARDING_DESIGN.md',
            
            # System Documentation  
            'system_summary': 'FINAL-SYSTEM-SUMMARY.md',
            'system_audit': 'SYSTEM-AUDIT.md',
            'system_documentation': 'SYSTEM-DOCUMENTATION.md',
            'execution_guide': 'STEP-BY-STEP-EXECUTION-GUIDE.md',
            
            # Application Code
            'frontend_app': 'app/frontend/',
            'backend_app': 'app/backend/',
            'package_json': 'app/frontend/package.json',
            'main_backend': 'app/backend/main.py',
            'strategic_engine': 'app/backend/strategic_workflow_engine.py',
            'context_manager': 'app/backend/context_manager.py',
            
            # Demo Scripts
            'demo_scripts': [
                'pm33_demo.py',
                'pm33_demo_openai.py', 
                'pm33_multi_engine_demo.py',
                'interactive-demo-app.py',
                'ask-strategic-ai.py'
            ]
        }
    
    def get_time_of_day(self):
        """Get appropriate greeting based on time"""
        hour = datetime.now().hour
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"
    
    def check_file_status(self):
        """Check which files exist and their modification status"""
        file_status = {
            'existing': [],
            'missing': [],
            'recent': []
        }
        
        import time
        current_time = time.time()
        
        for category, files in self.file_registry.items():
            if isinstance(files, list):
                for file_path in files:
                    if os.path.exists(file_path):
                        file_status['existing'].append(file_path)
                        # Check if modified in last 7 days
                        mod_time = os.path.getmtime(file_path)
                        if (current_time - mod_time) < (7 * 24 * 3600):
                            file_status['recent'].append(file_path)
                    else:
                        file_status['missing'].append(file_path)
            else:
                file_path = files
                if os.path.exists(file_path):
                    file_status['existing'].append(file_path)
                    # Check if modified in last 7 days
                    if os.path.isfile(file_path):
                        mod_time = os.path.getmtime(file_path)
                        if (current_time - mod_time) < (7 * 24 * 3600):
                            file_status['recent'].append(file_path)
                else:
                    file_status['missing'].append(file_path)
        
        return file_status
    
    def display_file_status(self, file_status):
        """Display file registry status for agents"""
        print("\n📁 FILE REGISTRY STATUS")
        print("=" * 40)
        
        if file_status['recent']:
            print(f"🔥 RECENTLY MODIFIED ({len(file_status['recent'])}):")
            for file_path in sorted(file_status['recent'][:5]):  # Show top 5
                print(f"   → {file_path}")
            if len(file_status['recent']) > 5:
                print(f"   ... and {len(file_status['recent']) - 5} more")
            print()
        
        if file_status['missing']:
            print(f"⚠️  MISSING FILES ({len(file_status['missing'])}):")
            for file_path in sorted(file_status['missing'][:3]):  # Show top 3
                print(f"   → {file_path}")
            if len(file_status['missing']) > 3:
                print(f"   ... and {len(file_status['missing']) - 3} more")
            print()
        
        print(f"✅ Total files tracked: {len(file_status['existing'])}")
        print()
    
    def session_startup(self):
        """Complete session startup with operational + strategic context"""
        os.system('clear')
        print("🚀 PM33 PMO Transformation with Agentic AI Teams - Session Manager")
        print("=" * 80)
        print(f"📅 Session Start: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        print("=" * 80)
        print()
        
        # Project status
        print("📍 OPERATIONAL STATUS")
        print("=" * 40)
        print(f"Location: {os.getcwd()}")
        
        # Check .env file
        if os.path.exists(".env"):
            with open(".env", 'r') as f:
                api_count = len([line for line in f if '=' in line and not line.strip().startswith('#')])
            print(f"🔑 API Keys: {api_count} configured in .env")
        else:
            print("❌ No .env file found!")
        
        # Database status
        print("🗄️  Database: Railway PostgreSQL")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            db_url = os.getenv('DATABASE_URL', 'Not configured')
            print(f"   Connection: {db_url[:30]}...")
        except:
            print("   Connection: Check .env configuration")
        
        print()
        
        # Strategic Context
        self.load_strategic_context()
        
        # Claude Context Summary
        print("\n" + "=" * 80)
        print("📋 COPY THIS CONTEXT TO CLAUDE SESSION:")
        print("=" * 80)
        
        context = f"""
🎯 PM33 PMO Transformation with Agentic AI Teams

CURRENT STATUS:
- Project: PMO transformation with fully functional agentic AI teams
- Goal: $100K MRR by Dec 31, 2025 (20-week execution plan)
- Vision: Transform PMs into PMOs through agentic AI teams
- Architecture: Services-based SAAS (FastAPI + PostgreSQL + Multi-AI)
- Foundation: Proven API sync + intelligent mapping patterns from Replit

AGENTIC AI TEAMS:
- Strategic Intelligence AI: Real-time analysis, competitive intelligence
- Workflow Execution AI: Task creation, cross-functional coordination  
- Data Intelligence AI: Context learning, predictive analytics
- Communication AI: Stakeholder management, executive reporting

PROVEN WORKFLOW PATTERNS (From Replit Solution):
✅ API-based Jira sync: Reliable data extraction and processing
✅ Intelligent field mapping: AI-powered with confidence scoring
✅ Database loading: Efficient work item storage and organization
✅ Actionable filtering: Smart filtering of work items for PM focus
❌ OAuth integration: Incomplete (use API tokens instead)
❌ Roadmap optimization/UX: Incomplete (build fresh)

DEMO & MARKETING STATUS:
✅ Next.js frontend app with Tailwind CSS (app/frontend/)
✅ Strategic chat backend API (app/backend/)  
✅ Comprehensive demo design (PM33_CLICKABLE_DEMO_DESIGN.md)
✅ UX architecture plan (PM33_UX_ARCHITECTURE_PLAN.md)
✅ Demo positioning guide (DEMO-POSITIONING-GUIDE.md)
✅ Development testing guide (DEVELOPMENT-TESTING-GUIDE.md)
⚠️  Interactive demo needs gamification + framework visualization
⚠️  Company context integration for personalized demos needed

ORGANIC GROWTH STRATEGY:
- Community-driven content across Reddit, LinkedIn, X, YouTube
- Authentic peer engagement vs corporate marketing
- Content templates for sustainable growth

TECHNICAL STATUS:
- Location: {os.getcwd()}
- Database: Railway PostgreSQL connected
- Multi-AI: Claude, OpenAI, Together AI configured
- Services: Resend (email), PostHog (analytics), Pinecone (vector DB)

VALUE PROPOSITION:
"Transform PMs into PMOs through agentic AI teams - driving product-led growth via strategic automation and improved execution alignment"

DIFFERENTIATOR:
"Transforms individual PMs into fully functional PMOs with AI-powered strategic teams"

Ready for development focused on proven patterns and agentic AI capabilities!
"""
        
        print(context)
        print("=" * 80)
        print()
        
        # Show file registry status
        file_status = self.check_file_status()
        self.display_file_status(file_status)
        
        print("🎯 SESSION READY!")
        print(f"Good {self.get_time_of_day()}! Context loaded - ready for development! 🚀")
        print()
        print("💡 KEY FILES FOR AGENTS:")
        print("   → Core context: INSTRUCTIONS-FOR-FUTURE-AGENTS.md")
        print("   → Design system guide: app/frontend/PM33_DESIGN_SYSTEM_GUIDE.md")
        print("   → Marketing design system: app/frontend/MARKETING_DESIGN_SYSTEM.md")
        print("   → App design system: app/frontend/APP_DESIGN_SYSTEM.md")
        print("   → Design enforcement: app/frontend/design-system-implementation.md")
        print("   → Demo design: PM33_CLICKABLE_DEMO_DESIGN.md")
        print("   → UX architecture: PM33_UX_ARCHITECTURE_PLAN.md")
        print("   → Demo positioning: DEMO-POSITIONING-GUIDE.md")
        print("   → Testing guide: DEVELOPMENT-TESTING-GUIDE.md")
        print("   → Marketing plan: marketing/DAY3-BETA-OUTREACH-PLAN.md")
        print("   → Frontend app: app/frontend/")
        print("   → Backend app: app/backend/")
        print()
        print("💡 SESSION MANAGEMENT:")
        print("   → At session end: python3 pm33-session-manager.py --end")
        print("   → Focus on proven Replit patterns, avoid OAuth/UX/import workflows")
        print()
    
    def load_strategic_context(self):
        """Load comprehensive strategic context (from context loader)"""
        print("🎯 STRATEGIC CONTEXT")
        print("=" * 40)
        print("""
MISSION: Transform PMs into fully functional PMOs through agentic AI teams that 
handle strategic intelligence, competitive analysis, and workflow execution.

CORE PROBLEM SOLVED: PMs need PMO-level strategic capabilities but lack the team, 
budget, and infrastructure - PM33 provides agentic AI teams that deliver PMO functionality.

KEY CAPABILITIES REQUIRED:
1. Strategic Intelligence Engine
   - Multi-AI strategic analysis (Claude, OpenAI, Together)
   - Context-aware decision support with confidence scoring
   - Competitive intelligence and response planning

2. Workflow Execution AI Team  
   - Automated task creation from strategic decisions
   - Cross-functional coordination and timeline management
   - PM tool integration with proven sync patterns

3. Data Intelligence AI Team
   - Company-specific context learning and preservation
   - Historical decision pattern recognition  
   - Predictive analytics for strategic planning

4. Communication AI Team
   - Stakeholder communication assistance
   - Executive summary generation
   - Cross-team alignment facilitation

SERVICES ARCHITECTURE:
🏗️ Core Infrastructure: Railway (PostgreSQL), Pinecone (Vector DB), Supabase (Backend)
🤖 AI Orchestration: Claude (Strategic Lead), OpenAI (Workflow), Together AI (Data)
📊 Analytics Layer: PostHog (User Analytics), Resend (Email), Stripe (Payments)
🔗 External Tools: Jira/Linear/Monday/Asana APIs (Proven Replit patterns)

SERVICE-AI TEAM MAPPING:
- Strategic Intelligence: Claude + Pinecone + PostHog
- Workflow Execution: OpenAI + Railway + PM Tool APIs  
- Data Intelligence: Together AI + Pinecone + Railway
- Communication: Claude/OpenAI + Resend + Railway

🧠 AI DEVELOPMENT ETHOS (Self-Improving Agents):
- Think Hard, Write Short: Deep analysis + concise execution + agent learning
- Update Before Create: Enhance existing first + smart enhancement discovery
- Industry-Leading Quality: Scalable solutions + predictive optimization
- Playwright-Driven UX: Continuous testing + automated A/B optimization
- Agent Self-Improvement: Cross-agent learning + new agent suggestion + client value acceleration

🎨 UI/UX DESIGN STRATEGY (Strategic Clarity Through Progressive Intelligence):
- Design Philosophy: Intelligence-first design that demonstrates AI capabilities through interface
- Architectural Separation: Marketing website (bold, conversion-focused) vs App (clean, productivity-focused)
- Brand Identity: Strategic Blue (#1E40AF), Growth Green (#059669), Innovation Orange (#EA580C)
- Enforcement: Multi-layer validation ensuring design system usage (not just documentation)
- Professional Innovation: Enterprise-ready aesthetics with forward-thinking AI interaction patterns
""")
        
        print("STRATEGIC PRIORITIES (20-week plan):")
        print("- Weeks 1-5: Agentic AI Foundation + services-based SAAS architecture")
        print("- Weeks 6-10: PMO Capabilities + data intelligence integration")  
        print("- Weeks 11-15: Advanced AI teams + communication capabilities")
        print("- Weeks 16-20: Enterprise features + PMO transformation leadership")
        print()
        
        print("PROVISIONED SERVICES STATUS:")
        print("✅ All configured with API keys in .env:")
        print("   - AI: Anthropic Claude, OpenAI, Together AI")
        print("   - Infrastructure: Railway PostgreSQL, Pinecone, Resend, PostHog")
        print("   - Frontend: Supabase, Stripe (payment processing)")
        print("   - Authentication: API tokens (NOT OAuth - OAuth failed)")
        print()
        
        print("SUCCESS METRICS:")
        print("- Revenue: $100K MRR by EOY 2025")
        print("- Capability: PMO-level functionality delivery")
        print("- Performance: 85% strategic success rate")
        print("- Efficiency: 300% PM capability improvement")
    
    def session_shutdown(self):
        """Interactive session end update checker"""
        os.system('clear')
        print("🔄 PM33 Session End Update - Ensuring Context Accuracy")
        print("=" * 80)
        print(f"📅 Session End: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        print("=" * 80)
        print()
        
        print("🔍 SESSION CONTEXT UPDATE CHECKLIST:")
        print("=" * 50)
        print()
        
        # Interactive checklist
        changes = {}
        
        print("1️⃣ PROJECT VISION & GOALS:")
        print("   Current: PMO transformation with agentic AI teams → $100K MRR by EOY 2025")
        changes['vision'] = input("   Has the core vision or revenue target changed? (y/N): ").lower().startswith('y')
        
        print("\n2️⃣ TECHNICAL ARCHITECTURE:")
        print("   Current: FastAPI + PostgreSQL + Multi-AI (Claude, OpenAI, Together)")
        changes['tech'] = input("   Did the tech stack or architecture change? (y/N): ").lower().startswith('y')
        
        print("\n3️⃣ DEVELOPMENT PHASE:")
        print("   Current: Building agentic AI teams using proven Replit patterns")
        changes['phase'] = input("   Did development focus or current phase shift? (y/N): ").lower().startswith('y')
        
        print("\n4️⃣ NEW DOCUMENTATION:")
        print("   File Registry tracks:", len([f for files in self.file_registry.values() 
                                               for f in (files if isinstance(files, list) else [files])]), "files")
        changes['docs'] = input("   Were any major new documents created this session? (y/N): ").lower().startswith('y')
        
        if changes['docs']:
            print("   📝 Please manually update file_registry in pm33-session-manager.py")
            print("   → Add new files to appropriate category in build_file_registry()")
        
        print("\n5️⃣ SUCCESS METRICS:")
        print("   Current: PMO-level capability delivery, 85% strategic success rate")
        changes['metrics'] = input("   Did success metrics or KPIs change? (y/N): ").lower().startswith('y')
        
        print("\n" + "=" * 50)
        
        # Determine if updates needed
        needs_update = any(changes.values())
        
        if needs_update:
            print("\n🚨 UPDATES NEEDED!")
            print("=" * 30)
            print("\n⚠️  Session manager needs updating based on your responses:")
            
            update_areas = []
            if changes['vision']:
                update_areas.append("→ Vision/Goals: Update PROJECT OVERVIEW and mission")
            if changes['tech']:
                update_areas.append("→ Architecture: Update technical status sections")
            if changes['phase']:
                update_areas.append("→ Phase: Update STRATEGIC PRIORITIES")
            if changes['docs']:
                update_areas.append("→ Documentation: Add new files to references")
            if changes['metrics']:
                update_areas.append("→ Metrics: Update SUCCESS METRICS")
            
            for area in update_areas:
                print(f"   {area}")
            
            print(f"\n📋 FILE TO UPDATE:")
            print(f"   → {__file__} (this session manager)")
            print(f"   → Update 'Last Updated' timestamp in header")
            
            edit_now = input("\n🔧 Open file for editing now? (y/N): ").lower().startswith('y')
            
            if edit_now:
                try:
                    if subprocess.run(['which', 'code'], capture_output=True).returncode == 0:
                        subprocess.run(['code', __file__])
                    else:
                        subprocess.run(['nano', __file__])
                except:
                    print(f"   Please manually edit: {__file__}")
            
            print("\n✅ REMEMBER TO:")
            print("   1. Update 'Last Updated' timestamp in file header")
            print("   2. Test the session manager runs without errors")
            print("   3. Commit changes with descriptive message")
            
        else:
            print("\n✅ NO UPDATES NEEDED!")
            print("=" * 30)
            print("\n🎯 Session manager is current and accurate.")
            print("   Your next session will have up-to-date context.")
        
        print(f"\n📊 CURRENT SESSION SUMMARY:")
        print("=" * 40)
        print("   Project: PM33 PMO Transformation")
        print("   Target: $100K MRR by EOY 2025") 
        print("   Architecture: Services-based SAAS with agentic AI")
        print("   Last Updated: 2025-08-18 (unified session management)")
        
        if not needs_update:
            print(f"\n🚀 READY FOR NEXT SESSION:")
            print("=" * 35)
            print("   Context is current. Next session startup:")
            print("   → python3 pm33-session-manager.py --start")
            print("   → Continue development with accurate context!")
            print("   → New agents: Read INSTRUCTIONS-FOR-FUTURE-AGENTS.md first")
        
        print(f"\n🎯 Session end complete! Happy coding! 🚀")
        print()

def main():
    """Main entry point with argument handling"""
    manager = PM33SessionManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--start':
            manager.session_startup()
        elif sys.argv[1] == '--end':
            manager.session_shutdown()
        elif sys.argv[1] == '--help':
            print("PM33 Session Manager")
            print("Usage:")
            print("  python pm33-session-manager.py --start    # Session startup")  
            print("  python pm33-session-manager.py --end      # Session shutdown")
            print("  python pm33-session-manager.py --help     # Show this help")
        else:
            print("Unknown argument. Use --help for usage info.")
    else:
        # Default behavior - session startup
        manager.session_startup()

if __name__ == "__main__":
    main()