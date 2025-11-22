# AI Song Generator — Complete Scaffold Upgrade

This upgrade adds a full reference scaffold for a Suno-style UI, end-to-end mock pipeline, BPM/tempo support, voice uploads with FFmpeg, and orchestration hooks.

Quick start (mock-mode):
- Requirements: Docker + Docker Compose
- Run: docker-compose up
- Frontend: http://localhost:3000 (Vite dev)
- Backend: http://localhost:8000

Environment variables:
- MOCK_MODE=true|false (default true)
- BLUEFLAME_API_KEY=your_api_key_here (only required when MOCK_MODE=false)
- DATABASE_URL / DATABASE_NAME (optional; pre-wired helpers available)
- Frontend uses VITE_BACKEND_URL to reach the backend

Features included:
- Dark Suno-style UI with purple (#7c3aed) and cyan (#06b6d4) accents
- Tempo (BPM) input, passed to every backend call and prompts
- Lyrics box, Voice selector (Male/Female presets + Custom upload with consent)
- Instrument panel with per-track controls (volume, pan, reverb, etc.)
- Timeline grid reflecting BPM, lyric markers placeholder
- Mood selector with multi-toggle
- Create pipeline orchestrating Instrumental → Melody → Vocal → Mix → Video with progress
- Playback with per-track mute/solo placeholders and download links when ready
- Mock-mode returns canned asset URLs and simulates progress
- Voice upload route accepts WAV/MP3/AMR; rejects <0.5s
- Orchestrator module with 7 prompts stored in blueflame_prompts.json (tempo-aware)
- Dockerfile includes FFmpeg; docker-compose binds mock assets and sets MOCK_MODE=true
- Simple e2e mock script and OpenAPI stub

Switching to production (real Blue Flame):
- Set MOCK_MODE=false
- Set BLUEFLAME_API_KEY in backend environment
- Implement real HTTP calls in backend_orchestrator.py where indicated

Acceptance checklist:
- Backend runs and shows ffmpeg present (Dockerfile installs)
- POST /api/upload/voice accepts .amr and returns voiceProfileId
- POST /api/generate/create returns a jobId
- GET /api/job/:jobId/status progresses to done and returns masterUrl & videoUrl (mock)

Testing (mock e2e):
- Run: python tests/e2e_mock_run.py

OpenAPI stub:
- GET /openapi-stub (lists implemented endpoints)
