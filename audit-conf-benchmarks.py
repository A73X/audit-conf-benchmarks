#!/usr/bin/env python3
import argparse
from orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(
        prog="audit-conf-benchmarks",
        description="Run audit checks against a benchmark (PDF or XLSX) and a given working directory."
    )

    parser.add_argument(
        "-b",
        "--benchmark",
        required=True,
        help="Path to the benchmark file (PDF or XLSX)."
    )

    parser.add_argument(
        "-w",
        "--workdir",
        required=True,
        help="Path to the working directory containing files to audit."
    )

    parser.add_argument(
        "-d",
        "--use-defaults",
        action="store_true",
        default=False,
        help="Evaluate compliance using the benchmark's documented default value when a key is not found on the machine."
    )

    args = parser.parse_args()

    benchmark_path = args.benchmark
    workdir = args.workdir

    orchestrator = Orchestrator(benchmark_path, workdir)
    orchestrator.audit(use_defaults=args.use_defaults)

if __name__ == "__main__":
    main()