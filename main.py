import argparse
from dataclasses import asdict

from configs.settings import PipelineSettings
from scripts.orchestration.pipeline import process_all


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Odia AI Educational Platform data pipeline.")
    parser.add_argument("--parallel", action="store_true", help="Process multiple PDFs concurrently.")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes.")
    parser.add_argument("--force", action="store_true", help="Rebuild outputs even when they exist.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_settings = PipelineSettings()
    settings = PipelineSettings(
        **{
            **asdict(base_settings),
            "max_workers": args.workers or base_settings.max_workers,
            "force": args.force,
        }
    )
    process_all(settings=settings, parallel=args.parallel)


if __name__ == "__main__":
    main()
