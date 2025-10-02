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

    args = parser.parse_args()

    benchmark_path = args.benchmark
    workdir = args.workdir

    orchestrator = Orchestrator(benchmark_path, workdir)
    orchestrator.audit()

if __name__ == "__main__":
    main()