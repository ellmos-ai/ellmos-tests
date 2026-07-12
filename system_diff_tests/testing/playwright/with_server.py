#!/usr/bin/env python3
"""Start one or more servers, wait for ports, run a command, then clean up."""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import time


def is_server_ready(port: int, timeout: int = 30) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run command after local server startup")
    parser.add_argument("--server", action="append", dest="servers", required=True)
    parser.add_argument("--port", action="append", dest="ports", type=int, required=True)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        print("Error: no command specified")
        sys.exit(2)
    if len(args.servers) != len(args.ports):
        print("Error: --server and --port counts must match")
        sys.exit(2)

    processes: list[subprocess.Popen] = []
    try:
        for index, (server_command, port) in enumerate(zip(args.servers, args.ports), start=1):
            print(f"Starting server {index}/{len(args.servers)}: {server_command}")
            process = subprocess.Popen(server_command, shell=True)
            processes.append(process)
            print(f"Waiting for localhost:{port}")
            if not is_server_ready(port, args.timeout):
                raise RuntimeError(f"server did not open port {port} within {args.timeout}s")

        result = subprocess.run(command)
        sys.exit(result.returncode)
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
