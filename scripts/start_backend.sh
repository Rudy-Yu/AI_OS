#!/bin/bash
set -e
export PYTHONPATH="$(pwd)"
uvicorn backend.main:app --reload --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"

