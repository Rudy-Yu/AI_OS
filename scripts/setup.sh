#!/bin/bash
echo "🚀 Setting up AI_OS..."
pip install -r requirements.txt
cp .env.example .env
mkdir -p logs chroma_db
touch config/active_version.json
echo '{"version": "v1"}' > config/active_version.json
echo "✅ Setup complete! Edit .env lalu jalankan start_backend.sh"

