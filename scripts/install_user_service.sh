#!/usr/bin/env bash
# Installs a systemd --user service that runs the Streamlit BI chatbot demo
# persistently, bound to 127.0.0.1:8501, for remote access through Tailscale Serve.
#
# Idempotent: safe to re-run. Does not use sudo or touch system-wide services.
# Enabling "linger" (so the service survives logout / starts at boot) requires
# root; if we can't get it non-interactively we print the exact command to run.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_DIR}/.venv"
UNIT_NAME="bi-chatbot-demo.service"
UNIT_TEMPLATE="${REPO_DIR}/deploy/systemd/user/${UNIT_NAME}"
PORT=8501
REAL_HOME="$(getent passwd "$(id -un)" | cut -d: -f6)"
USER_UNIT_DIR="${REAL_HOME}/.config/systemd/user"
USER_UNIT_PATH="${USER_UNIT_DIR}/${UNIT_NAME}"

log() { printf '==> %s\n' "$1"; }

# --- sanity checks -----------------------------------------------------
if [[ ! -f "${UNIT_TEMPLATE}" ]]; then
    echo "error: unit template not found at ${UNIT_TEMPLATE}" >&2
    exit 1
fi

if [[ ! -x "${VENV_DIR}/bin/streamlit" ]]; then
    log "Repo venv not found or missing streamlit at ${VENV_DIR}"
    log "Create it first:"
    echo "    python3 -m venv \"${VENV_DIR}\""
    echo "    \"${VENV_DIR}/bin/pip\" install -r \"${REPO_DIR}/requirements.txt\""
    exit 1
fi

# --- build the DuckDB warehouse first -----------------------------------
log "Building DuckDB warehouse from synthetic CSVs..."
"${VENV_DIR}/bin/python" "${REPO_DIR}/scripts/build_duckdb.py"

# --- render the unit file -----------------------------------------------
log "Installing user unit to ${USER_UNIT_PATH}"
mkdir -p "${USER_UNIT_DIR}"
sed \
    -e "s#__REPO_DIR__#${REPO_DIR}#g" \
    -e "s#__VENV_DIR__#${VENV_DIR}#g" \
    "${UNIT_TEMPLATE}" > "${USER_UNIT_PATH}"

# --- enable + (re)start the service --------------------------------------
systemctl --user daemon-reload
systemctl --user enable "${UNIT_NAME}"
systemctl --user restart "${UNIT_NAME}"

log "Service status:"
systemctl --user --no-pager status "${UNIT_NAME}" || true

# --- linger: lets the user service run without an active login session ---
# and start automatically at boot. Requires root, so we try loginctl first
# and fall back to a clear instruction rather than invoking sudo ourselves.
CURRENT_USER="$(id -un)"
LINGER_STATE="$(loginctl show-user "${CURRENT_USER}" -p Linger --value 2>/dev/null || echo "unknown")"

if [[ "${LINGER_STATE}" == "yes" ]]; then
    log "Linger already enabled for ${CURRENT_USER} (service will survive logout/reboot)."
elif loginctl enable-linger "${CURRENT_USER}" >/dev/null 2>&1; then
    log "Linger enabled for ${CURRENT_USER}."
else
    log "Could not enable linger without elevated privileges (this script does not run sudo)."
    echo "    To make the service survive logout and start automatically at boot, run:"
    echo "        sudo loginctl enable-linger ${CURRENT_USER}"
fi

# --- print access URLs ----------------------------------------------------
log "Streamlit BI chatbot demo is listening on 127.0.0.1:${PORT}"

if command -v tailscale >/dev/null 2>&1; then
    log "Publishing through Tailscale Serve on HTTPS port ${PORT} (tailnet only)..."
    tailscale serve --bg --yes --https="${PORT}" "${PORT}" >/dev/null 2>&1 || \
        log "Could not configure Tailscale Serve automatically. Run: tailscale serve --bg --https=${PORT} ${PORT}"
fi

TS_IP="$(tailscale ip -4 2>/dev/null | head -1 || true)"
TS_DNS="$(tailscale status --json 2>/dev/null | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    name = d.get("Self", {}).get("DNSName", "").rstrip(".")
    if name:
        print(name)
except Exception:
    pass
' 2>/dev/null || true)"

if [[ -n "${TS_DNS}" ]]; then
    echo "    MagicDNS URL: https://${TS_DNS}:${PORT}"
fi
if [[ -n "${TS_IP}" ]]; then
    echo "    Local HTTP fallback over Tailscale IP: http://${TS_IP}:${PORT}"
fi
if [[ -z "${TS_DNS}" && -z "${TS_IP}" ]]; then
    log "Tailscale not detected/running. Install and 'tailscale up' to get a remote URL."
fi

log "Note: Streamlit itself binds only to localhost; Tailscale Serve exposes it inside your tailnet."

log "Useful commands:"
echo "    systemctl --user status ${UNIT_NAME}"
echo "    systemctl --user restart ${UNIT_NAME}"
echo "    journalctl --user -u ${UNIT_NAME} -f"
