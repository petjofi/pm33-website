#!/bin/bash

# PM33 Claude Code Session Starter
# Run this script to quickly resume work and provide Claude with full context
#
# ⚠️ IMPORTANT: Keep this file updated whenever project status changes!
# Update sections: PROJECT STATUS, TECHNICAL STATUS, VALUE PROP, DIFFERENTIATOR
# Last Updated: 2025-08-18 (PMO transformation vision correction)

clear
echo "🚀 PM33 PMO Transformation with Agentic AI Teams - Session Starter"
echo "=============================================="
echo ""

# Navigate to project directory
cd /Users/ssaper/Desktop/my-projects/pm33-claude-execution

# Show current project status
echo "📍 Project Location: $(pwd)"
echo "📅 Date: $(date '+%A, %B %d, %Y')"
echo "⏰ Time: $(date '+%I:%M %p')"
echo ""

# Check if .env exists and count API keys
if [ -f ".env" ]; then
    api_count=$(grep -c "=" .env)
    echo "🔑 API Keys: $api_count configured in .env"
else
    echo "❌ No .env file found!"
fi

# Check database connection quickly
echo "🗄️  Database: Railway PostgreSQL"
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL', 'Not configured')
print(f'   Connection: {db_url[:30]}...')
" 2>/dev/null

echo ""
echo "==================== CURRENT WEEK STATUS ===================="

# Show current week progress
python3 actions/daily-agent.py status 2>/dev/null || echo "Daily agent not ready yet"

echo ""
echo "==================== TODAY'S TASKS =========================="

# Generate or show today's tasks
TODAY_FILE="actions/daily-tasks-$(date +%Y-%m-%d).md"

if [ -f "$TODAY_FILE" ]; then
    echo "✅ Today's tasks already generated"
    echo "📋 Task Summary:"
    grep -E "^- \[ \]" "$TODAY_FILE" | head -5 | sed 's/^/   /'
    if [ $(grep -c "^- \[ \]" "$TODAY_FILE") -gt 5 ]; then
        echo "   ... and $(($(grep -c "^- \[ \]" "$TODAY_FILE") - 5)) more tasks"
    fi
else
    echo "🔄 Generating today's tasks..."
    python3 actions/daily-agent.py generate >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Tasks generated successfully"
        grep -E "^- \[ \]" "$TODAY_FILE" | head -3 | sed 's/^/   /'
    else
        echo "❌ Could not generate tasks"
    fi
fi

echo ""
echo "==================== CONTEXT FOR CLAUDE ===================="
echo ""
echo "📋 COPY THIS CONTEXT TO NEW CLAUDE SESSION:"
echo "-----------------------------------------------------------"
cat << 'EOF'

We're working on PM33 PMO Transformation with Agentic AI Teams - transforming PMs into PMOs with fully functional agentic AI teams.

CURRENT STATUS:
- Project: PM33 PMO Transformation (Services-based SAAS with agentic AI teams)
- Goal: $100K MRR by Dec 31, 2025 (20-week execution plan)
- Focus: Building agentic AI teams that provide PMO-level capabilities
- Architecture: FastAPI + PostgreSQL + Multi-AI (Claude, OpenAI, Together)
- Foundation: Proven API sync + intelligent mapping patterns from Replit solution

TECHNICAL STATUS:
- Location: /Users/ssaper/Desktop/my-projects/pm33-claude-execution
- Database: Railway PostgreSQL connected  
- API Keys: All configured (Anthropic, Resend, PostHog, Pinecone)
- Dependencies: Python packages installed
- Environment: .env file configured with all keys

KEY CONTEXT FILES (read these for full context):
1. /strategy/execution-plan/pm33-strategic-recommendations.md (main strategy)
2. /actions/week-1-execution-commands.md (detailed commands)  
3. /strategy/competitive-analysis/market-research-key-findings.md (market research)
4. /actions/daily-tasks-$(date +%Y-%m-%d).md (today's specific tasks)

IMMEDIATE NEXT STEPS:
1. Check today's tasks: python3 actions/daily-agent.py generate
2. Execute Day 2 commands: Strategic AI Chat API + React component
3. Focus: Build core differentiator (AI chat with workflow generation)

VALUE PROP: "PMO-level capabilities at PM budget through agentic AI teams"
DIFFERENTIATOR: Transforms individual PMs into fully functional PMOs with AI-powered strategic teams

Ready to continue execution!
EOF

echo "-----------------------------------------------------------"
echo ""

# Show key files that exist
echo "📁 KEY FILES AVAILABLE:"
echo "   ✅ Strategy: strategy/execution-plan/pm33-strategic-recommendations.md"
echo "   ✅ Commands: actions/week-1-execution-commands.md" 
echo "   ✅ Research: strategy/competitive-analysis/market-research-key-findings.md"
echo "   ✅ Today's Tasks: $TODAY_FILE"
echo "   ✅ Environment: .env (all API keys configured)"
echo ""

# Quick commands reference  
echo "==================== QUICK COMMANDS ======================="
echo ""
echo "📋 Daily Management:"
echo "   python3 actions/daily-agent.py generate     # Get today's tasks"
echo "   python3 actions/daily-agent.py status       # Check week progress"
echo "   python3 actions/daily-agent.py complete <id> # Mark task done"
echo ""
echo "🔧 Development:"
echo "   cd app/backend && python3 strategic-workflow-engine.py  # Test AI engine"
echo "   python3 -m uvicorn app.backend.main:app --reload       # Start API server"
echo ""
echo "📄 View Files:"
echo "   cat strategy/execution-plan/pm33-strategic-recommendations.md"
echo "   cat actions/week-1-execution-commands.md"
echo "   cat $TODAY_FILE"
echo ""

# Check if we need to continue from specific day
CURRENT_HOUR=$(date +%H)
if [ $CURRENT_HOUR -lt 12 ]; then
    TIME_OF_DAY="morning"
elif [ $CURRENT_HOUR -lt 17 ]; then
    TIME_OF_DAY="afternoon"  
else
    TIME_OF_DAY="evening"
fi

echo "🎯 READY TO CONTINUE EXECUTION!"
echo "Good $TIME_OF_DAY! Next steps:"
echo ""
echo "1️⃣ Copy the context above to Claude for immediate session context"
echo "2️⃣ Run: python PM33_COMPLETE_CONTEXT_LOADER.py (for full strategic context)"
echo "3️⃣ Ready to build PM33 PMO transformation! 🚀"
echo ""
echo "⚠️  REMINDER: Update context files if anything changes during session!"
echo "   Last updated: 2025-08-18 (PMO transformation vision correction)"
echo "   End of session: Run ./session-end-update.sh to ensure context accuracy"
echo ""