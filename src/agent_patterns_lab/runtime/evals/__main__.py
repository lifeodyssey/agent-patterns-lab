from __future__ import annotations

import argparse
import sys

from agent_patterns_lab.runtime.adapters.anthropic_model import AnthropicMessagesModel, MissingOptionalDependency as AnthropicMissing
from agent_patterns_lab.runtime.adapters.openai_model import MissingOptionalDependency as OpenAIMissing
from agent_patterns_lab.runtime.adapters.openai_model import OpenAIChatModel

from .runner import run_eval_suite
from .tasks import all_tasks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline-first eval harness for agent_patterns_lab.")
    parser.add_argument("--mode", choices=["offline", "openai", "anthropic"], default="offline")
    parser.add_argument("--model", default=None, help="Model name for live modes.")
    parser.add_argument("--out-dir", default=".evals")
    parser.add_argument("--trace-dir", default=".traces/evals")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--baseline", default=None, help="Baseline JSON to diff against.")
    args = parser.parse_args(argv)

    mode = args.mode
    live_factory = None

    if mode == "openai":
        model_name = args.model or "gpt-4o-mini"
        try:
            live_model = OpenAIChatModel(model=model_name, trace_content=False)
        except OpenAIMissing as e:
            print(str(e), file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Failed to init OpenAI model: {e}", file=sys.stderr)
            return 2

        live_factory = lambda _role: live_model

    if mode == "anthropic":
        model_name = args.model or "claude-3-5-sonnet-latest"
        try:
            live_model = AnthropicMessagesModel(model=model_name, trace_content=False)
        except AnthropicMissing as e:
            print(str(e), file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Failed to init Anthropic model: {e}", file=sys.stderr)
            return 2

        live_factory = lambda _role: live_model

    summary, _outcomes, _meta = run_eval_suite(
        all_tasks(),
        out_dir=args.out_dir,
        trace_dir=args.trace_dir,
        data_dir=args.data_dir,
        mode=mode,
        live_model_factory=live_factory,
        baseline_json=args.baseline,
    )

    print(
        f"done: total={summary.total} pass={summary.passed} fail={summary.failed} error={summary.errored} skip={summary.skipped} duration={summary.duration_s:.3f}s"
    )
    print(f"reports: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

