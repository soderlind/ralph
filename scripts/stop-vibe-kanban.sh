#!/bin/bash
# Stop all running Vibe-Kanban UI processes
#
# This script kills all vibe-kanban processes that were started with `npm run vibe-kanban` or `npx vibe-kanban`
# Usage: ./scripts/stop-vibe-kanban.sh

echo "🛑 Stopping Vibe-Kanban UI processes..."
echo ""

# Function to check if processes exist
has_vibe_kanban() {
    ps aux | grep -i "vibe-kanban" | grep -v grep > /dev/null 2>&1
    return $?
}

# Check if there are any vibe-kanban processes
if ! has_vibe_kanban; then
    echo "✅ No Vibe-Kanban processes found. Already stopped."
    exit 0
fi

echo "📋 Running Vibe-Kanban processes:"
ps aux | grep -i "vibe-kanban" | grep -v grep || echo "   None"
echo ""

# Kill vibe-kanban processes by PID
echo "🔧 Stopping vibe-kanban processes..."
ps aux | grep -i "vibe-kanban" | grep -v grep | awk '{print $2}' | while read PID; do
    if [ -n "$PID" ]; then
        echo "  ⏳ Killing process $PID"
        kill $PID 2>/dev/null || true
    fi
done

sleep 1

# Try harder if needed
if has_vibe_kanban; then
    echo "⚠️  Some processes still running, forcing termination..."
    ps aux | grep -i "vibe-kanban" | grep -v grep | awk '{print $2}' | while read PID; do
        if [ -n "$PID" ]; then
            kill -9 $PID 2>/dev/null || true
        fi
    done
    sleep 1
fi

# Final check
if has_vibe_kanban; then
    echo "❌ Failed to stop all Vibe-Kanban processes"
    echo "   Remaining processes:"
    ps aux | grep -i "vibe-kanban" | grep -v grep
    exit 1
else
    echo "✅ All Vibe-Kanban processes stopped successfully"
    exit 0
fi
