# PM33 Actions & Task Management

This directory contains automated task management and daily workflow tools for the PM33 execution plan.

## Daily Agent System

The `daily-agent.py` script provides intelligent task management that adapts to your flexible work schedule.

### Features

- **Flexible Scheduling**: Works with 5+ days per week, supports working 2-3 days ahead
- **Smart Task Distribution**: Different task types for each day of the week
- **Progress Tracking**: Automatic logging of completed tasks and progress notes
- **Weekly Objectives**: Integration with the overall PM33 execution plan
- **Intelligent Prioritization**: High/medium/low priority task scheduling

### Quick Start

Generate today's tasks:
```bash
python actions/daily-agent.py generate
```

Generate tomorrow's tasks (for planning ahead):
```bash
python actions/daily-agent.py generate --days-ahead 1
```

Mark a task as complete:
```bash
python actions/daily-agent.py complete w1t3 --notes "MCP server successfully migrated"
```

Add a progress note:
```bash
python actions/daily-agent.py note "Made significant progress on automation hooks setup"
```

Check weekly status:
```bash
python actions/daily-agent.py status
```

## Daily Workflow Pattern

### Monday: Week Planning & High-Priority Development
- Review week objectives
- Focus on critical development tasks
- Start major migrations/setups

### Tuesday: Development Continuation & Automation
- Continue high-priority tasks
- Begin automation configuration
- Deep focus work

### Wednesday: Mid-Week Review & Medium Priority
- Progress review and adjustment
- Work on medium priority items
- Course correction if needed

### Thursday: High-Priority Completion
- Complete remaining critical tasks
- Setup monitoring systems
- Prepare for week-end

### Friday: Week Completion & Next Week Prep
- Finish remaining tasks
- Week wrap-up review
- Next week planning

### Weekend: Strategic & Light Development
- **Saturday**: Strategic review, light development
- **Sunday**: Next week planning, preparation

## File Structure

```
actions/
├── README.md                    # This file
├── daily-agent.py              # Main daily task agent
├── current-tasks.json          # Today's current tasks
├── progress-log.json           # Historical progress log
├── weekly-tracker.json         # Weekly objectives and KPIs
└── daily-tasks-YYYY-MM-DD.md   # Generated daily task files
```

## Task Management Data

The system maintains three key data files:

### current-tasks.json
Stores today's active tasks, completion status, and notes.

### progress-log.json
Historical log of:
- Daily task completions
- Progress notes
- Performance metrics
- Weekly summaries

### weekly-tracker.json
Current week objectives including:
- Week 1-20 execution plan tasks
- KPI targets and current status
- Task priorities and dependencies

## Integration with PM33 Execution Plan

The daily agent automatically pulls from your Week 1 objectives:

**Week 1 (Aug 18-24) Tasks:**
- ✅ Create unified workspace structure
- ✅ Setup master Claude Code configuration  
- ⏳ Migrate MCP server from pm33-ai-native
- ⏳ Migrate strategy files from PM33
- ⏳ Migrate website assets from pm33-website
- ⏳ Configure automation hooks
- ⏳ Deploy initial monitoring

## Advanced Usage

### Working Multiple Days Ahead
If you want to batch work for 2-3 days:

```bash
# Generate tasks for next 3 days
python actions/daily-agent.py generate --days-ahead 0 > today.md
python actions/daily-agent.py generate --days-ahead 1 > tomorrow.md  
python actions/daily-agent.py generate --days-ahead 2 > day-after.md
```

### Custom Task Scheduling
The agent intelligently schedules based on:
- Day of the week
- Task priority (high/medium/low)
- Task type (development/automation/planning/review)
- Current week objectives
- Historical completion patterns

### Progress Tracking
Tasks are automatically tracked with:
- Completion timestamps
- Progress notes
- Weekly completion rates
- KPI progress against targets

## Automation Integration

The daily agent integrates with the broader PM33 automation system:
- Updates are logged to the main execution tracker
- Progress feeds into marketing automation metrics
- Completion data drives next week's planning
- KPI tracking feeds into revenue progression monitoring

## Troubleshooting

### Common Issues

**"No tasks generated"**: Check that weekly-tracker.json exists and has current week data.

**"Task ID not found"**: Use `python actions/daily-agent.py status` to see all available task IDs.

**"Permission denied"**: Make sure daily-agent.py is executable: `chmod +x actions/daily-agent.py`

### Data Recovery

All data files use JSON format for easy manual editing if needed. Backup files are created automatically before major updates.

### Reset Daily Tasks
To reset and regenerate tasks:
```bash
rm actions/current-tasks.json
python actions/daily-agent.py generate
```

## Future Enhancements

- Integration with external task management tools (Notion, Todoist)
- Slack/Discord notifications for task reminders
- Time tracking and productivity analytics
- Automated task scheduling based on calendar availability
- Machine learning-based task duration estimation