#!/bin/bash
#
# Autonomous Evolution Cron Job
# Runs every 10 minutes to execute meaningful evolution work
#

set -euo pipefail

# Configuration
DSLMODEL_PATH="/Users/sac/dev/dslmodel"
PYTHON_ENV="/Users/sac/dev/uvmgr/.venv/bin/python"
LOG_DIR="${DSLMODEL_PATH}/logs"
LOCK_FILE="${DSLMODEL_PATH}/.evolution_cron.lock"
PID_FILE="${DSLMODEL_PATH}/.evolution_cron.pid"

# Create log directory
mkdir -p "${LOG_DIR}"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_DIR}/evolution_cron.log"
}

# Function to clean up on exit
cleanup() {
    local exit_code=$?
    if [[ -f "${LOCK_FILE}" ]]; then
        rm -f "${LOCK_FILE}"
    fi
    if [[ -f "${PID_FILE}" ]]; then
        rm -f "${PID_FILE}"
    fi
    log "Cron job finished with exit code: ${exit_code}"
    exit ${exit_code}
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Check if another instance is running
if [[ -f "${LOCK_FILE}" ]]; then
    if [[ -f "${PID_FILE}" ]]; then
        local pid
        pid=$(<"${PID_FILE}")
        if kill -0 "${pid}" 2>/dev/null; then
            log "Another evolution cron job is still running (PID: ${pid}), skipping this run"
            exit 0
        else
            log "Stale lock file found, removing and continuing"
            rm -f "${LOCK_FILE}" "${PID_FILE}"
        fi
    else
        log "Lock file found but no PID file, removing lock and continuing"
        rm -f "${LOCK_FILE}"
    fi
fi

# Create lock file
echo $$ > "${PID_FILE}"
touch "${LOCK_FILE}"

log "Starting autonomous evolution cron job"

# Change to project directory
cd "${DSLMODEL_PATH}"

# Verify environment
if [[ ! -f "${PYTHON_ENV}" ]]; then
    log "ERROR: Python environment not found at ${PYTHON_ENV}"
    exit 1
fi

if [[ ! -f "src/dslmodel/commands/autonomous_evolution_daemon.py" ]]; then
    log "ERROR: Autonomous evolution daemon not found"
    exit 1
fi

# Run single evolution cycle with timeout
log "Executing evolution cycle..."

timeout 540 "${PYTHON_ENV}" -m src.dslmodel.commands.autonomous_evolution_daemon simulate --cycles 1 --fast 2>&1 | \
    tee -a "${LOG_DIR}/evolution_cron.log" || {
    local exit_code=$?
    if [[ ${exit_code} -eq 124 ]]; then
        log "Evolution cycle timed out after 9 minutes"
    else
        log "Evolution cycle failed with exit code: ${exit_code}"
    fi
    exit ${exit_code}
}

log "Evolution cycle completed successfully"

# Check disk space and clean up old logs if needed
if [[ $(df "${LOG_DIR}" | awk 'NR==2{print $5}' | sed 's/%//') -gt 90 ]]; then
    log "Disk space > 90%, cleaning up old logs"
    find "${LOG_DIR}" -name "*.log" -mtime +7 -delete
fi

# Rotate log file if it's too large (>10MB)
if [[ -f "${LOG_DIR}/evolution_cron.log" ]] && [[ $(stat -f%z "${LOG_DIR}/evolution_cron.log" 2>/dev/null || echo 0) -gt 10485760 ]]; then
    log "Rotating large log file"
    mv "${LOG_DIR}/evolution_cron.log" "${LOG_DIR}/evolution_cron_$(date +%Y%m%d_%H%M%S).log"
fi

log "Cron job completed successfully"