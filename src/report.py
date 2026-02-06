from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_config(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def generate_report(config: dict) -> str:
    output_dir = Path(config["output_dir"])
    summary_path = output_dir / "top_trigrams_summary.csv"
    counts_path = output_dir / "summary_counts.csv"

    if not summary_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {summary_path}")
    if not counts_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {counts_path}")

    top_ngrams = pd.read_csv(summary_path)
    counts = pd.read_csv(counts_path)

    lines = []
    lines.append("# Insights por idioma - Booking Reviews")
    lines.append("")
    lines.append("Relatório gerado a partir do pipeline NLP. Use este documento para interpretar os temas mais frequentes")
    lines.append("em reviews positivas e negativas por idioma.")
    lines.append("")

    for lang in config["target_languages"]:
        label = config.get("language_labels", {}).get(lang, lang)
        lines.append(f"## {label} ({lang})")

        lang_counts = counts[counts["language"] == lang]
        good_count = lang_counts[lang_counts["sentiment"] == "good"]["reviews"].sum()
        bad_count = lang_counts[lang_counts["sentiment"] == "bad"]["reviews"].sum()
        lines.append(f"- Reviews analisadas: **{int(good_count)} boas** | **{int(bad_count)} ruins**")

        for sentiment, title in [("good", "Temas positivos"), ("bad", "Temas negativos")]:
            lines.append(f"### {title}")
            subset = top_ngrams[(top_ngrams["language"] == lang) & (top_ngrams["sentiment"] == sentiment)]
            if subset.empty:
                lines.append("- Sem dados suficientes para este idioma.")
                continue
            for _, row in subset.head(10).iterrows():
                lines.append(f"- {row['ngram']} ({int(row['freq'])})")

        lines.append("")

    lines.append("## Implicações recomendadas")
    lines.append("- Compare temas positivos/negativos por idioma para ajustar comunicação e prioridades operacionais.")
    lines.append("- Investigue itens recorrentes negativos e valide com operações locais.")
    lines.append("- Use os temas positivos como insumo para mensagens de marketing segmentadas.")

    return "\n".join(lines).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Booking Reviews report")
    parser.add_argument("--config", default="config/config.json", help="Path to config.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    report_text = generate_report(config)
    report_path = Path(config["report_path"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8-sig")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
