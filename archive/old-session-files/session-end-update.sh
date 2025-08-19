#!/bin/bash

# PM33 End-of-Session Update Script
# Run this at the end of each development session to keep context files current

clear
echo "🔄 PM33 Session End Update - Ensuring Context Accuracy"
echo "======================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "PM33_COMPLETE_CONTEXT_LOADER.py" ]; then
    echo "❌ Error: Not in PM33 project directory"
    echo "   Please run from: /Users/ssaper/Desktop/my-projects/pm33-claude-execution"
    exit 1
fi

echo "📍 Project Location: $(pwd)"
echo "📅 Session End: $(date '+%A, %B %d, %Y at %I:%M %p')"
echo ""

# Interactive prompts to check if updates are needed
echo "🔍 SESSION CONTEXT UPDATE CHECKLIST:"
echo "======================================"
echo ""

# Check project vision/goals
echo "1️⃣ PROJECT VISION & GOALS:"
echo "   Current: PMO transformation with agentic AI teams → $100K MRR by EOY 2025"
read -p "   Has the core vision or revenue target changed? (y/N): " vision_changed

# Check technical architecture  
echo ""
echo "2️⃣ TECHNICAL ARCHITECTURE:"
echo "   Current: FastAPI + PostgreSQL + Multi-AI (Claude, OpenAI, Together)"
read -p "   Did the tech stack or architecture change? (y/N): " tech_changed

# Check development phase/focus
echo ""
echo "3️⃣ DEVELOPMENT PHASE:"
echo "   Current focus: Building agentic AI teams using proven Replit patterns"
read -p "   Did development focus or current phase shift? (y/N): " phase_changed

# Check new documentation
echo ""
echo "4️⃣ NEW DOCUMENTATION:"
read -p "   Were any major new documents created this session? (y/N): " docs_added

# Check success metrics
echo ""
echo "5️⃣ SUCCESS METRICS:"
echo "   Current: PMO-level capability delivery, 85% strategic success rate"
read -p "   Did success metrics or KPIs change? (y/N): " metrics_changed

echo ""
echo "========================================"

# Determine if updates are needed
needs_update="false"
if [[ "$vision_changed" =~ ^[Yy]$ ]] || [[ "$tech_changed" =~ ^[Yy]$ ]] || [[ "$phase_changed" =~ ^[Yy]$ ]] || [[ "$docs_added" =~ ^[Yy]$ ]] || [[ "$metrics_changed" =~ ^[Yy]$ ]]; then
    needs_update="true"
fi

if [ "$needs_update" = "true" ]; then
    echo ""
    echo "🚨 UPDATES NEEDED!"
    echo "=================="
    echo ""
    echo "⚠️  Context files need updating based on your responses:"
    
    if [[ "$vision_changed" =~ ^[Yy]$ ]]; then
        echo "   → Vision/Goals: Update PROJECT OVERVIEW in both files"
    fi
    
    if [[ "$tech_changed" =~ ^[Yy]$ ]]; then
        echo "   → Architecture: Update TECHNICAL STATUS sections"
    fi
    
    if [[ "$phase_changed" =~ ^[Yy]$ ]]; then
        echo "   → Phase: Update STRATEGIC PRIORITIES and current focus"
    fi
    
    if [[ "$docs_added" =~ ^[Yy]$ ]]; then
        echo "   → Documentation: Add new files to DOCUMENT REFERENCE GUIDE"
    fi
    
    if [[ "$metrics_changed" =~ ^[Yy]$ ]]; then
        echo "   → Metrics: Update SUCCESS METRICS sections"
    fi
    
    echo ""
    echo "📋 FILES TO UPDATE:"
    echo "   1. session-starter.sh (operational context)"
    echo "   2. PM33_COMPLETE_CONTEXT_LOADER.py (strategic context)"
    echo ""
    echo "📖 REFERENCE:"
    echo "   cat SESSION-FILES-MAINTENANCE.md (for detailed update instructions)"
    echo ""
    
    # Offer to open files for editing
    read -p "🔧 Open files for editing now? (y/N): " edit_now
    
    if [[ "$edit_now" =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔧 Opening files for editing..."
        
        # Try different editors based on availability
        if command -v code >/dev/null 2>&1; then
            code session-starter.sh PM33_COMPLETE_CONTEXT_LOADER.py SESSION-FILES-MAINTENANCE.md
        elif command -v nano >/dev/null 2>&1; then
            echo "   Opening with nano (Ctrl+X to exit each file)"
            nano session-starter.sh
            nano PM33_COMPLETE_CONTEXT_LOADER.py
        else
            echo "   No suitable editor found. Please manually edit:"
            echo "   - session-starter.sh"
            echo "   - PM33_COMPLETE_CONTEXT_LOADER.py"
        fi
    fi
    
    echo ""
    echo "✅ REMEMBER TO:"
    echo "   1. Update 'Last Updated' timestamps in both files"
    echo "   2. Test both files run without errors"
    echo "   3. Commit changes with descriptive message"
    
else
    echo ""
    echo "✅ NO UPDATES NEEDED!"
    echo "==================="
    echo ""
    echo "🎯 Context files are current and accurate."
    echo "   Your next session will have up-to-date context."
fi

echo ""
echo "📊 CURRENT SESSION SUMMARY:"
echo "=========================="
echo "   Project: PM33 PMO Transformation"
echo "   Target: $100K MRR by EOY 2025"
echo "   Architecture: Services-based SAAS with agentic AI"
echo "   Last Context Update: $(grep -o 'Last Updated: [0-9-]*' PM33_COMPLETE_CONTEXT_LOADER.py 2>/dev/null || echo 'Unknown')"
echo ""

# Reminder about fresh session benefits
if [ "$needs_update" = "false" ]; then
    echo "🚀 READY FOR NEXT SESSION:"
    echo "========================="
    echo "   Your context files are current. Next session startup:"
    echo "   1. ./session-starter.sh"
    echo "   2. python PM33_COMPLETE_CONTEXT_LOADER.py"
    echo "   3. Continue development with accurate context!"
fi

echo ""
echo "🎯 Session end update complete! Happy coding! 🚀"
echo ""