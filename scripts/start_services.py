#!/usr/bin/env python3
"""
Local AI Infrastructure - Service Startup Script

Usage:
    python start_services.py --profile gpu-nvidia
    python start_services.py --profile gpu-nvidia --environment public
    python start_services.py --profile cpu
    python start_services.py --profile gpu-amd

Profiles:
    gpu-nvidia  : NVIDIA GPU (requires nvidia-container-toolkit)
    gpu-amd     : AMD GPU (requires ROCm)
    cpu         : CPU-only mode

Environments:
    private     : (default) All ports accessible, for local/VPN use
    public      : Only ports 80/443 open, traffic via Caddy reverse proxy
"""

import argparse
import subprocess
import sys
import os
import shutil


def check_prerequisites():
    """Check that Docker and Docker Compose are installed."""
    if not shutil.which("docker"):
        print("[ERROR] Docker is not installed. Please install Docker first.")
        print("  -> https://docs.docker.com/engine/install/ubuntu/")
        sys.exit(1)

    result = subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[ERROR] Docker Compose V2 is not available.")
        print("  -> https://docs.docker.com/compose/install/")
        sys.exit(1)

    print("[OK] Docker and Docker Compose are available.")


def check_nvidia_gpu():
    """Check if NVIDIA GPU and container toolkit are available."""
    result = subprocess.run(
        ["nvidia-smi"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[WARN] nvidia-smi not found. GPU may not be available.")
        return False

    print("[OK] NVIDIA GPU detected:")
    for line in result.stdout.strip().split("\n")[:5]:
        print(f"  {line}")
    return True


def check_env_file():
    """Check if .env file exists, create from example if not."""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    env_example = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.example")

    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            shutil.copy2(env_example, env_file)
            print("[INFO] Created .env from .env.example")
            print("[WARN] Please edit .env and set your own secrets before continuing!")
            print(f"  -> {env_file}")
            sys.exit(1)
        else:
            print("[ERROR] No .env or .env.example found.")
            sys.exit(1)
    else:
        print("[OK] .env file found.")


def start_services(profile: str, environment: str):
    """Start Docker Compose services with the specified profile."""

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    profiles = [profile]
    if environment == "public":
        profiles.append("public")

    cmd = ["docker", "compose"]
    for p in profiles:
        cmd.extend(["--profile", p])
    cmd.extend(["up", "-d"])

    print(f"\n[INFO] Starting services with profile(s): {', '.join(profiles)}")
    print(f"[INFO] Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print(" LOCAL AI INFRASTRUCTURE - Services Started!")
        print("=" * 60)
        print()
        print(" Access your services:")
        if environment == "private":
            print(f"  Open WebUI:   http://localhost:8080")
            print(f"  N8N:          http://localhost:5678")
            print(f"  Supabase:     http://localhost:8000")
            print(f"  SearXNG:      http://localhost:8888")
            print(f"  Ollama API:   http://localhost:11434")
        else:
            print(f"  All services accessible via configured domains through Caddy")
            print(f"  (ports 80/443 only)")
        print()
        print(" Useful commands:")
        print(f"  View logs:    docker compose logs -f")
        print(f"  Stop:         docker compose --profile {profile} down")
        print(f"  Restart:      docker compose --profile {profile} restart")
        print("=" * 60)
    else:
        print(f"\n[ERROR] Failed to start services. Exit code: {result.returncode}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Local AI Infrastructure - Service Manager"
    )
    parser.add_argument(
        "--profile",
        choices=["gpu-nvidia", "gpu-amd", "cpu"],
        required=True,
        help="GPU profile to use"
    )
    parser.add_argument(
        "--environment",
        choices=["private", "public"],
        default="private",
        help="Deployment environment (default: private)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(" LOCAL AI INFRASTRUCTURE - Startup")
    print("=" * 60)
    print()

    check_prerequisites()
    check_env_file()

    if args.profile == "gpu-nvidia":
        check_nvidia_gpu()

    start_services(args.profile, args.environment)


if __name__ == "__main__":
    main()
