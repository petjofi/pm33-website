# Session Files Maintenance Guide

## 🎯 **Purpose**
Keep `session-starter.sh` and `PM33_COMPLETE_CONTEXT_LOADER.py` accurate and current throughout development.

---

## 📋 **Update Triggers**

### **Always Update When:**
- ✅ **Project vision changes** (like PMO transformation correction)
- ✅ **Goals or targets shift** ($100K MRR, timelines, success metrics)
- ✅ **Technical architecture evolves** (new services, integrations, frameworks)
- ✅ **New major documentation created** (PRDs, strategy docs, workflow guides)
- ✅ **Phase transitions** (Week 1 → Week 2, MVP → Beta, etc.)
- ✅ **Key insights discovered** (like Replit proven patterns)

### **Monthly Reviews:**
- Check if all document references still exist and are current
- Verify technical status sections match actual implementation
- Update success metrics if targets have evolved
- Refresh "Last Updated" timestamps

---

## 🔧 **What to Update in Each File**

### **`session-starter.sh` Updates:**
```bash
# Update these sections when they change:
- Line 7: Main project title/vision
- Lines 75-82: CURRENT STATUS section  
- Lines 102-103: VALUE PROP and DIFFERENTIATOR
- Lines 160-161: Last updated timestamp
- Lines 92-96: KEY CONTEXT FILES paths
```

### **`PM33_COMPLETE_CONTEXT_LOADER.py` Updates:**
```python
# Update these sections when they change:
- Lines 6-12: Header maintenance instructions
- Lines 21-28: PROJECT OVERVIEW mission and goals
- Lines 135-147: STRATEGIC PRIORITIES phases and metrics
- Lines 166-248: Document reference lists (add new files)
- Lines 269-302: SUCCESS METRICS targets
- Line 313: Last updated timestamp
```

---

## ⚡ **Quick Update Checklist**

When something major changes in the project:

### **Step 1: Identify Impact**
- [ ] Does this change the core mission/vision?
- [ ] Does this affect the technical architecture?
- [ ] Does this create new documentation?
- [ ] Does this change success metrics or timelines?

### **Step 2: Update Files**
- [ ] Update `session-starter.sh` context section
- [ ] Update `PM33_COMPLETE_CONTEXT_LOADER.py` relevant sections
- [ ] Update "Last Updated" timestamps in both files
- [ ] Test both files to ensure they run without errors

### **Step 3: Document Changes**
- [ ] Add brief change note in file headers
- [ ] Update any related documentation references
- [ ] Commit changes with clear commit message

---

## 🎯 **Integration with Development**

### **During Sessions:**
- If Claude identifies outdated information, update files immediately
- If new major insights emerge, add them to context loader
- If project pivots or evolves, update both files before next session

### **Weekly Reviews:**
- Check if document references need updating
- Verify technical status matches current implementation
- Update progress indicators and current focus areas

### **Major Milestones:**
- Update phase information when transitioning
- Refresh success metrics if targets evolved
- Add new proven patterns or insights discovered

---

## 🚀 **Benefits of Keeping Updated**

### **For You:**
- Always have current context ready for new Claude sessions
- Quick reference to project status and next steps
- Historical record of project evolution

### **For Claude:**
- Accurate context leads to better recommendations
- Reduced need to correct outdated assumptions
- More relevant suggestions based on current reality

### **For Project:**
- Maintains strategic alignment across all development
- Prevents drift from original goals and vision
- Documents evolution and decision history

---

**Remember**: These files are your project's memory system. Keep them as current and accurate as your codebase!