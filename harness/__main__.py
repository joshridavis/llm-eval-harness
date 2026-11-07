import argparse
import json
import sys
from pathlib import Path

from harness.cases import load_suite
from harness.runner import run_suite


def main():
    parser = argparse.ArgumentParser(prog="harness")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("--suite", required=True)
    run.add_argument("--prompt", required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--judge-model", required=True)
    run.add_argument("--runs", type=int, default=5)
    run.add_argument("--out", required=True)

    args = parser.parse_args()

    if args.command == "run":
        suite = load_suite(Path("suites") / args.suite, args.prompt)
        result = run_suite(suite, args.prompt, args.model, args.judge_model, args.runs)
        Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        for case in result["cases"]:
            print(f"{case['verdict']:<12} {case['pass_rate']:.0%}  {case['id']}")
        return 0


if __name__ == "__main__":
    sys.exit(main())