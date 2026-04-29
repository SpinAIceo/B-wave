# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

B-Wave is an Edge-Vision AI ship PSC (Port State Control) defect auto-diagnosis scanner by Spinai. Crew members point a waterproof tablet camera at ship equipment; the system detects defects (corrosion, leaks, damage, missing labels) in real-time via an edge server and overlays PSC violation codes on screen. All core functions must work fully offline.

## Architecture

Four major systems, three languages:

1. **Edge AI Engine** (Python) — FastAPI server on industrial mini PC running YOLOv8/TensorRT inference, PSC regulation rule engine (SQLite), gRPC endpoint for tablet communication. Must meet <500ms inference latency. Runs Ubuntu Server on ARM64/x86_64, containerized with Docker.

2. **Mobile Viewer App** (Dart/Flutter) — Cross-platform BYOD app. Streams camera frames to edge server via gRPC, renders 2D bounding box overlays (CustomPainter), caches results offline (Hive/Isar). Targets Android 11+ / iOS 16+.

3. **Fleet View Dashboard** (TypeScript/React) — Land-based monitoring dashboard with D3.js charts and Mapbox maps. Connects to FastAPI backend with PostgreSQL + TimescaleDB. Syncs with edge servers when satellite connectivity restores.

4. **Mesh Network** — 802.11s Wi-Fi mesh connecting tablets to edge server through steel bulkheads. No code in this repo; hardware/AP configuration only.

## Key Constraints

- **Offline-first**: Every core feature must work without internet. Edge server is the single source of truth at sea.
- **OT network write prohibition**: Ship OT network is read-only via unidirectional API. Never write to OT systems.
- **Cyber security**: Must comply with IMO UR E26/E27 and IACS cyber resilience requirements. TLS 1.3, RBAC, audit logging mandatory.
- **COTS hardware only**: No custom hardware manufacturing. Use commercial off-the-shelf industrial mini PCs and consumer tablets.

## Tech Stack Summary

| Layer | Stack |
|---|---|
| AI training | PyTorch, transfer learning from medical imaging models |
| AI inference (edge) | ONNX → TensorRT, YOLOv8 custom |
| Edge server | Python, FastAPI, gRPC, SQLite, Docker |
| Mobile app | Flutter (Dart), gRPC client |
| Land backend | Python, FastAPI, PostgreSQL, TimescaleDB |
| Land frontend | React, TypeScript, D3.js, Mapbox GL JS |
| CI/CD | GitHub Actions, Docker |
| Security | TLS 1.3, JWT + RBAC, unidirectional data diode |
