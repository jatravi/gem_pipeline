import sys

from app.pipelines.gem_discovery_pipeline import run_gem_pipeline


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    summary = run_gem_pipeline(limit=limit)
    print(f"\nExit status: {summary.get('run_status', 'unknown')}")


if __name__ == "__main__":
    main()