#!/bin/bash

# PM33 Daily Task Auto-Update Script
# Automatically generates daily tasks and sets up for tomorrow

PROJECT_ROOT="/Users/ssaper/Desktop/my-projects/pm33-claude-execution"
cd "$PROJECT_ROOT"

# Generate today's tasks if not already generated
TODAY=$(date +%Y-%m-%d)
TODAY_FILE="actions/daily-tasks-$TODAY.md"

if [ ! -f "$TODAY_FILE" ]; then
    echo "🔄 Generating tasks for today ($TODAY)..."
    python3 actions/daily-agent.py generate
    echo "✅ Today's tasks generated: $TODAY_FILE"
else
    echo "✅ Today's tasks already exist: $TODAY_FILE"
fi

# Generate tomorrow's tasks for planning ahead
TOMORROW=$(date -v+1d +%Y-%m-%d)
TOMORROW_FILE="actions/daily-tasks-$TOMORROW.md"

if [ ! -f "$TOMORROW_FILE" ]; then
    echo "🔄 Generating tasks for tomorrow ($TOMORROW)..."
    python3 actions/daily-agent.py generate --days-ahead 1
    echo "✅ Tomorrow's tasks generated: $TOMORROW_FILE"
else
    echo "✅ Tomorrow's tasks already exist: $TOMORROW_FILE"
fi

# Show current week status
echo ""
echo "📊 Current Week Status:"
python3 actions/daily-agent.py status

# Show today's task summary
echo ""
echo "📋 Today's Task Summary:"
if [ -f "$TODAY_FILE" ]; then
    grep -E "^- \[ \]" "$TODAY_FILE" | head -5
    echo ""
    echo "📄 Full tasks: $TODAY_FILE"
else
    echo "❌ No tasks file found for today"
fi

echo ""
echo "🔄 Auto-update complete!"
echo ""
echo "Quick commands:"
echo "• Mark task complete: python3 actions/daily-agent.py complete <task_id> --notes 'done'"
echo "• Add progress note: python3 actions/daily-agent.py note 'progress update'"
echo "• Manual task generation: python3 actions/daily-agent.py generate"