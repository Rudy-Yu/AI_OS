#!/bin/bash
# Usage: ./scripts/upgrade_version.sh v1 v2
FROM=$1
TO=$2
cp -r ai_versions/$FROM ai_versions/$TO
echo "✅ Berhasil copy $FROM → $TO"
echo "📝 Sekarang edit ai_versions/$TO/brain.py untuk tambah fitur baru"
echo "🔄 Untuk aktifkan: echo '{\"version\": \"$TO\"}' > config/active_version.json"

