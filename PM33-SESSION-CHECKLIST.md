# PM33 Session Startup & Shutdown Checklist

## 🚀 **SESSION STARTUP CHECKLIST**

### **Before Each Development Session:**

#### **Step 1: Navigate to Project**
```bash
cd /Users/ssaper/Desktop/my-projects/pm33-claude-execution
```

#### **Step 2: Run Unified Session Manager**
```bash
python3 pm33-session-manager.py --start
```
*or simply:*
```bash
python3 pm33-session-manager.py
```

#### **Step 3: Copy Context to Claude**
- ✅ Copy the generated context block to new Claude session
- ✅ Verify all key information is current and accurate
- ✅ Confirm technical status shows correct database/API connections

#### **Step 4: Ready Check**
- ✅ Project location correct
- ✅ API keys configured (shown in startup)
- ✅ Database connection verified
- ✅ Claude has complete context
- ✅ Ready to begin development!

---

## 🔄 **SESSION SHUTDOWN CHECKLIST**

### **At End of Each Development Session:**

#### **Step 1: Run Session End Check**
```bash
python3 pm33-session-manager.py --end
```

#### **Step 2: Interactive Update Review**
Answer honestly about changes during the session:
- ✅ **Project Vision & Goals** - Did core mission or targets change?
- ✅ **Technical Architecture** - Did tech stack or services change?  
- ✅ **Development Phase** - Did focus area or current phase shift?
- ✅ **New Documentation** - Were major new files/docs created?
- ✅ **Success Metrics** - Did KPIs or success criteria change?

#### **Step 3: Update Session Manager (If Needed)**
If changes occurred:
- ✅ Edit `pm33-session-manager.py` with new information
- ✅ Update "Last Updated" timestamp in file header
- ✅ Test the session manager runs without errors
- ✅ Save changes

#### **Step 4: Commit Changes**
```bash
git add pm33-session-manager.py
git commit -m "Update session context: [brief description of changes]"
```

#### **Step 5: Session Complete**
- ✅ Context files updated and accurate
- ✅ Changes committed to git
- ✅ Next session will have current context
- ✅ Ready for efficient startup next time!

---

## 📋 **QUICK REFERENCE**

### **Daily Commands:**
```bash
# Start development session
python3 pm33-session-manager.py --start

# End development session  
python3 pm33-session-manager.py --end

# Help/usage info
python3 pm33-session-manager.py --help
```

### **File Management:**
- **`pm33-session-manager.py`** - Single file containing all session logic
- **Old files to remove**: `session-starter.sh`, `PM33_COMPLETE_CONTEXT_LOADER.py`, `session-end-update.sh`
- **Keep updated**: Only the session manager needs maintenance

### **What Gets Updated:**
When project changes, update these sections in `pm33-session-manager.py`:
- **PROJECT OVERVIEW** - Mission, goals, problem statement
- **STRATEGIC CONTEXT** - Priorities, phases, capabilities  
- **TECHNICAL STATUS** - Architecture, services, integrations
- **SUCCESS METRICS** - Targets, KPIs, timeline
- **CLAUDE CONTEXT** - Summary block that gets copied

---

## 🎯 **BENEFITS OF UNIFIED APPROACH**

### **Simplified Workflow:**
- ✅ **One file to maintain** instead of multiple scripts
- ✅ **Integrated startup/shutdown** in single command
- ✅ **Consistent context** between sessions
- ✅ **Automatic accuracy checks** built-in

### **Better Maintenance:**
- ✅ **Single source of truth** for all session context
- ✅ **Interactive update detection** prevents outdated info
- ✅ **Version control friendly** - track changes in one file
- ✅ **Self-documenting** - all context in one place

### **Efficient Development:**
- ✅ **Faster session startup** - complete context in seconds
- ✅ **Accurate Claude context** - always current information
- ✅ **Clean memory usage** - optimized for development flow
- ✅ **Change tracking** - know when context needs updates

---

## 🚨 **IMPORTANT REMINDERS**

### **Always Update When:**
- Core vision or mission changes
- Revenue targets or timelines shift
- Technical architecture evolves
- Major new documentation created
- Success metrics or KPIs change
- Development phase transitions

### **Never Skip:**
- Session end update check (catches forgotten changes)
- Testing session manager after updates
- Committing changes to version control
- Updating timestamp after modifications

### **Best Practices:**
- Run session end check even for short sessions
- Be honest about changes during interactive review
- Keep context concise but comprehensive
- Update immediately when changes occur (don't wait)

---

**Remember: Accurate session context = Efficient development + Better Claude assistance! 🚀**