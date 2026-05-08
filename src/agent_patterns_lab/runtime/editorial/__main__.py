from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent_patterns_lab.runtime import Tracer
from agent_patterns_lab.runtime.adapters.anthropic_model import (
    AnthropicMessagesModel,
    MissingOptionalDependency as AnthropicMissing,
)
from agent_patterns_lab.runtime.adapters.openai_model import (
    MissingOptionalDependency as OpenAIMissing,
    OpenAIChatModel,
)

from .pipeline import EditorialPipeline, render_aggregate_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="review→revise→polish pipeline for docs (rubric-scored).")
    parser.add_argument("--mode", choices=["offline", "openai", "anthropic"], default="offline")
    parser.add_argument("--model", default=None, help="Model name for live modes.")
    parser.add_argument("--locale", choices=["en", "zh", "auto"], default="auto")
    parser.add_argument("--input", default="docs", help="A markdown file or a directory (default: docs).")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help='Exclude paths containing this substring (repeatable). Example: --exclude "docs/superpowers".',
    )
    parser.add_argument("--out-dir", default=".editorial")
    parser.add_argument("--apply", action="store_true", help="Overwrite source markdown files in-place.")
    parser.add_argument("--trace-dir", default=".traces/editorial")
    args = parser.parse_args(argv)

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"input not found: {in_path}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    trace_dir = Path(args.trace_dir)

    mode = args.mode
    locale = args.locale

    tracer = Tracer()

    pipeline = _make_pipeline(mode=mode, model_name=args.model, locale=locale, tracer=tracer)

    md_files = _collect_markdown(in_path, excludes=list(args.exclude))
    if not md_files:
        print("no markdown files found", file=sys.stderr)
        return 2

    results = []
    for p in md_files:
        doc_locale = _infer_locale(p) if locale == "auto" else locale
        effective = pipeline if pipeline.locale == doc_locale else _make_pipeline(
            mode=mode, model_name=args.model, locale=doc_locale, tracer=tracer
        )
        text = p.read_text(encoding="utf-8")
        res = effective.run(path=p, markdown=text)
        effective.write_outputs(result=res, out_dir=out_dir, apply_to_source=args.apply)
        results.append(res)

    (out_dir / "REPORT.md").write_text(render_aggregate_report(results), encoding="utf-8")
    tracer.export_jsonl(trace_dir / "editorial.jsonl")

    print(f"done: files={len(results)} mode={mode} out={out_dir}")
    if args.apply:
        print("applied: source markdown overwritten")
    else:
        print(f"rewritten copies: {out_dir}/out/")
    print(f"report: {out_dir}/REPORT.md")
    print(f"trace: {trace_dir}/editorial.jsonl")
    return 0


def _collect_markdown(path: Path, *, excludes: list[str]) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() == ".md" else []
    out: list[Path] = []
    for p in sorted(path.rglob("*.md")):
        # Skip generated site output if someone points to repo root.
        if "site" in p.parts:
            continue
        # Skip internal/meta docs that aren't part of the public site map.
        if "superpowers" in p.parts:
            continue
        # Skip template placeholders like `_template.md`.
        if p.name.startswith("_"):
            continue
        sp = str(p)
        if any(x and x in sp for x in excludes):
            continue
        out.append(p)
    return out


def _infer_locale(path: Path) -> str:
    parts = set(path.parts)
    if "zh" in parts:
        return "zh"
    return "en"


def _make_pipeline(*, mode: str, model_name: str | None, locale: str, tracer: Tracer) -> EditorialPipeline:
    if mode == "offline":
        return EditorialPipeline(mode="offline", locale=locale, tracer=tracer)

    if mode == "openai":
        name = model_name or "gpt-4o-mini"
        try:
            m = OpenAIChatModel(model=name, trace_content=False, temperature=0.2, max_tokens=2000)
        except OpenAIMissing as e:
            raise SystemExit(str(e))
        return EditorialPipeline(mode="live", locale=locale, writer=m, reviewer=m, polisher=m, tracer=tracer)

    # anthropic
    name = model_name or "claude-3-5-sonnet-latest"
    try:
        m = AnthropicMessagesModel(model=name, trace_content=False, temperature=0.2, max_tokens=2000)
    except AnthropicMissing as e:
        raise SystemExit(str(e))
    return EditorialPipeline(mode="live", locale=locale, writer=m, reviewer=m, polisher=m, tracer=tracer)


if __name__ == "__main__":
    raise SystemExit(main())
