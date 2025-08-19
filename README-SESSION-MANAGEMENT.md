# PM33 Session Management Guide

## 🚀 Quick Session Restart

### **Method 1: Automatic (Recommended)**
```bash
# Run the session starter script
./session-starter.sh
```

This will:
- ✅ Show current project status
- ✅ Generate today's tasks  
- ✅ Display context for new Claude session
- ✅ Show quick commands reference

### **Method 2: Manual**
```bash
cd /Users/ssaper/Desktop/my-projects/pm33-claude-execution
python3 actions/daily-agent.py status
python3 actions/daily-agent.py generate
```

## 📋 Context for New Claude Sessions

**Copy and paste this to new Claude:**

```
We're working on PM33 Strategic AI Co-Pilot - targeting $100K MRR.

CURRENT STATUS:
- Week 1 infrastructure setup completed 
- Next: Day 2 Strategic AI Chat implementation
- Location: /Users/ssaper/Desktop/my-projects/pm33-claude-execution

KEY FILES TO READ:
1. /strategy/execution-plan/pm33-strategic-recommendations.md
2. /actions/week-1-execution-commands.md  
3. Current day tasks: /actions/daily-tasks-YYYY-MM-DD.md

TECHNICAL STATUS:
- Database: Railway PostgreSQL connected
- APIs: All configured in .env
- Dependencies: All Python packages installed

Ready to continue execution!
```

## 🔄 Daily Workflow

### **Starting Each Day:**
1. `./session-starter.sh` - Get full status
2. `python3 actions/daily-agent.py generate` - Get today's tasks
3. Start execution

### **During Work:**
```bash
# Mark tasks complete
python3 actions/daily-agent.py complete <task-id> --notes "completed successfully"

# Add progress notes  
python3 actions/daily-agent.py note "made good progress on API endpoint"

# Check status anytime
python3 actions/daily-agent.py status
```

### **End of Day:**
```bash
# Review progress
python3 actions/daily-agent.py status

# Generate tomorrow's tasks
python3 actions/daily-agent.py generate --days-ahead 1
```

## 🧠 Memory Management

### **When Claude Runs Out of Memory:**

#### **Option A: Create Progress Checkpoint**
```bash
# Generate comprehensive status
python3 actions/daily-agent.py status > current-progress.md
echo "## Environment Status" >> current-progress.md
echo "- All API keys configured in .env" >> current-progress.md  
echo "- Database: Railway PostgreSQL connected" >> current-progress.md
echo "- Location: $(pwd)" >> current-progress.md
```

#### **Option B: Use Session Starter**
```bash
./session-starter.sh
# Copy the "CONTEXT FOR CLAUDE" section to new session
```

#### **Option C: Key Files Reference**
Tell new Claude to read these essential files:
- `/strategy/execution-plan/pm33-strategic-recommendations.md` (complete strategy)
- `/actions/week-1-execution-commands.md` (all commands)
- Current day's task file for specific next steps

## 📁 Important File Locations

### **Never Lose These:**
```bash
.env                                    # All API keys
strategy/execution-plan/               # Complete strategy docs
actions/week-1-execution-commands.md   # All execution commands
actions/daily-tasks-*.md               # Daily task files
app/backend/strategic-workflow-engine.py # Core AI engine
```

### **Quick File Checks:**
```bash
# Verify key files exist
ls -la .env strategy/execution-plan/ actions/week-1-execution-commands.md

# Check API key count
grep -c "=" .env

# View current tasks
cat actions/daily-tasks-$(date +%Y-%m-%d).md
```

## 🆘 Emergency Recovery

### **If Something Goes Wrong:**
```bash
# Check project status
./session-starter.sh

# Verify environment
python3 -c "from dotenv import load_dotenv; load_dotenv(); print('✅ Environment loaded')"

# Test database
python3 -c "
import asyncpg, asyncio, os
from dotenv import load_dotenv
load_dotenv()
async def test(): 
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    print('✅ Database connected')
    await conn.close()
asyncio.run(test())
"

# Check daily agent
python3 actions/daily-agent.py status
```

### **If Daily Agent Breaks:**
```bash
# Manual task check
cat actions/weekly-tracker.json
cat actions/current-tasks.json

# Regenerate if needed
rm actions/*.json
python3 actions/daily-agent.py generate
```

## 💡 Pro Tips

### **Terminal Session Management:**
- Keep one terminal tab open in the project directory
- Use `./session-starter.sh` after breaks
- Always check status before starting new work

### **Claude Memory Optimization:**
- Start new sessions every 50+ messages
- Use session-starter.sh context every time  
- Reference key files instead of re-explaining strategy

### **Progress Tracking:**
- Mark tasks complete immediately after finishing
- Add progress notes for complex work
- Check weekly status regularly

## 🎯 Quick Reference Card

```bash
# Essential Commands (memorize these)
./session-starter.sh                    # Full session restart
python3 actions/daily-agent.py generate # Get today's tasks  
python3 actions/daily-agent.py status   # Check progress
python3 actions/daily-agent.py complete <id> # Mark done

# Key Files (always reference these)
strategy/execution-plan/pm33-strategic-recommendations.md
actions/week-1-execution-commands.md
actions/daily-tasks-$(date +%Y-%m-%d).md
```

**You're now set up for seamless session management! 🚀**