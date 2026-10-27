#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse
import time

RATE_LIMIT_KEYWORDS = [
    "rate limit",
    "ratelimit",
    "resource_exhausted",
    "resourceexhausted",
    "quota exceeded",
    "429 too many requests",
    "too many requests",
    "insufficient_quota",
    "overloaded",
    "service unavailable",
]

def run_command_streaming(cmd, log_fp):
    print(f"Executing: {' '.join(cmd)}")
    log_fp.write(f"Executing: {' '.join(cmd)}\n")
    log_fp.flush()
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    full_output = []
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write(line)
        sys.stdout.flush()
        log_fp.write(line)
        log_fp.flush()
        full_output.append(line)
        
    process.stdout.close()
    returncode = process.wait()
    output_str = "".join(full_output)
    return returncode, output_str

def is_rate_limited_or_unavailable(returncode, output_str):
    if returncode != 0:
        lower = output_str.lower()
        for kw in RATE_LIMIT_KEYWORDS:
            if kw in lower:
                return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Subagent runner with agy and codex fallback")
    parser.add_argument("--engine", choices=["agy", "codex", "agy-first"], default="agy-first", help="Execution engine")
    parser.add_argument("--prompt-file", required=True, help="File containing the prompt")
    parser.add_argument("--log-file", required=True, help="File to write logs to")
    parser.add_argument("--step-name", default="step", help="Name of current step")
    args = parser.parse_args()

    if not os.path.exists(args.prompt_file):
        print(f"Error: Prompt file {args.prompt_file} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(args.prompt_file, "r", encoding="utf-8") as f:
        prompt_content = f.read()

    os.makedirs(os.path.dirname(os.path.abspath(args.log_file)), exist_ok=True)
    log_fp = open(args.log_file, "a", encoding="utf-8")
    
    header = f"\n{'='*40}\nSTART STEP: {args.step_name} [{time.strftime('%Y-%m-%d %H:%M:%S')}]\nENGINE: {args.engine}\n{'='*40}\n"
    print(header)
    log_fp.write(header)
    log_fp.flush()

    agy_cmd = [
        "agy",
        "--dangerously-skip-permissions",
        "--model", "gemini-3.8-flash-medium",
        "-p", prompt_content
    ]

    codex_cmd = [
        "codex",
        "exec",
        "-m", "gpt-5.6-luna",
        "-c", "model_reasoning_effort=medium",
        prompt_content
    ]

    success = False
    
    if args.engine == "codex":
        rc, out = run_command_streaming(codex_cmd, log_fp)
        success = (rc == 0)
    elif args.engine == "agy":
        rc, out = run_command_streaming(agy_cmd, log_fp)
        success = (rc == 0)
    elif args.engine == "agy-first":
        rc, out = run_command_streaming(agy_cmd, log_fp)
        if rc == 0:
            success = True
        else:
            rate_limited = is_rate_limited_or_unavailable(rc, out)
            fallback_msg = f"\n[WARNING] agy failed with code {rc} (rate_limited={rate_limited}). Falling back to codex gpt-5.6-luna...\n"
            print(fallback_msg)
            log_fp.write(fallback_msg)
            log_fp.flush()
            
            rc, out = run_command_streaming(codex_cmd, log_fp)
            success = (rc == 0)

    footer = f"\n{'='*40}\nEND STEP: {args.step_name} [{time.strftime('%Y-%m-%d %H:%M:%S')}] - SUCCESS={success}\n{'='*40}\n"
    print(footer)
    log_fp.write(footer)
    log_fp.close()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
