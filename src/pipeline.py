from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd
import spacy

from spacy.lang.en.stop_words import STOP_WORDS as EN_STOPWORDS
from spacy.lang.de.stop_words import STOP_WORDS as DE_STOPWORDS
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOPWORDS

try:
    from langdetect import detect as langdetect
except Exception:  # optional dependency
    langdetect = None


STOPWORDS_MAP = {
    "en": EN_STOPWORDS,
    "de": DE_STOPWORDS,
    "fr": FR_STOPWORDS,
}

WORD_PATTERN = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ']+")


def load_config(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_language(lang: object) -> str | None:
    if lang is None:
        return None
    if isinstance(lang, float) and pd.isna(lang):
        return None
    value = str(lang).strip().lower()
    if not value:
        return None
    if "-" in value:
        value = value.split("-")[0]
    return value


def clean_text(text: object) -> str:
    if text is None:
        return ""
    value = str(text).replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def guess_language_by_stopwords(text: str, min_hits: int, targets: List[str]) -> str | None:
    words = set(WORD_PATTERN.findall(text.lower()))
    if not words:
        return None
    scores = {lang: len(words & STOPWORDS_MAP[lang]) for lang in targets}
    best_lang, best_score = max(scores.items(), key=lambda x: x[1])
    if best_score < min_hits:
        return None
    return best_lang


def detect_language(
    text: str,
    lang_hint: object,
    targets: List[str],
    fallback_cfg: dict,
) -> str | None:
    lang = normalize_language(lang_hint)
    if lang in targets:
        return lang

    if not fallback_cfg.get("enabled", True):
        return None

    if langdetect is not None:
        try:
            detected = langdetect(text)
            if detected in targets:
                return detected
        except Exception:
            pass

    return guess_language_by_stopwords(
        text,
        min_hits=fallback_cfg.get("min_stopword_hits", 2),
        targets=targets,
    )


def load_raw_reviews(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    hotel_ids = filters.get("hotel_ids") or []
    if hotel_ids:
        df = df[df["hotelId"].isin(hotel_ids)].copy()
    return df


def prepare_reviews(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    good_col = config["good_column"]
    bad_col = config["bad_column"]
    lang_col = config["language_column"]

    df = df[[lang_col, good_col, bad_col]].copy()
    df = df.rename(
        columns={
            good_col: "good",
            bad_col: "bad",
            lang_col: "lang_hint",
        }
    )

    long_df = df.melt(
        id_vars=["lang_hint"],
        value_vars=["good", "bad"],
        var_name="sentiment",
        value_name="text",
    )

    long_df["text"] = long_df["text"].apply(clean_text)
    long_df = long_df[long_df["text"].str.len() >= config.get("min_text_length", 15)]

    targets = config["target_languages"]
    fallback_cfg = config.get("language_fallback", {})

    long_df["language"] = long_df.apply(
        lambda row: detect_language(row["text"], row["lang_hint"], targets, fallback_cfg),
        axis=1,
    )

    long_df = long_df[long_df["language"].isin(targets)].copy()

    if config.get("drop_duplicates", True):
        long_df = long_df.drop_duplicates(subset=["language", "sentiment", "text"])

    return long_df


def load_spacy_models(config: dict) -> Dict[str, spacy.Language]:
    models = {}
    for lang, model_name in config["spacy_models"].items():
        try:
            models[lang] = spacy.load(model_name, disable=["ner", "parser"])
        except OSError as exc:
            raise OSError(
                f"spaCy model '{model_name}' not found. "
                f"Run: python -m spacy download {model_name}"
            ) from exc
    return models


def tokenize_docs(
    texts: Iterable[str],
    nlp: spacy.Language,
    allowed_pos: List[str],
    min_token_length: int,
) -> Iterable[List[str]]:
    for doc in nlp.pipe(texts, batch_size=200):
        tokens = []
        for token in doc:
            if token.is_stop or not token.is_alpha:
                continue
            if token.pos_ not in allowed_pos:
                continue
            lemma = token.lemma_.lower().strip()
            if len(lemma) < min_token_length:
                continue
            tokens.append(lemma)
        if tokens:
            yield tokens


def count_ngrams(tokens_iter: Iterable[List[str]], ngram_size: int) -> Counter:
    counter: Counter = Counter()
    for tokens in tokens_iter:
        for i in range(len(tokens) - ngram_size + 1):
            counter[tuple(tokens[i : i + ngram_size])] += 1
    return counter


def build_top_ngrams_df(
    counter: Counter,
    top_n: int,
    language: str,
    sentiment: str,
) -> pd.DataFrame:
    rows = [
        {
            "language": language,
            "sentiment": sentiment,
            "ngram": " ".join(ngram),
            "freq": freq,
        }
        for ngram, freq in counter.most_common(top_n)
    ]
    return pd.DataFrame(rows)


def run_pipeline(config: dict, write_outputs: bool = True) -> dict:
    input_path = Path(config["input_path"]).resolve()
    df = load_raw_reviews(input_path)
    df = apply_filters(df, config.get("filters", {}))

    reviews = prepare_reviews(df, config)
    counts = (
        reviews.groupby(["language", "sentiment"])
        .size()
        .reset_index(name="reviews")
        .sort_values(["language", "sentiment"])
    )

    models = load_spacy_models(config)
    allowed_pos = config.get("allowed_pos", ["ADJ", "NOUN", "PROPN"])
    min_token_length = config.get("min_token_length", 2)
    ngram_size = config.get("ngram_size", 3)
    top_n = config.get("top_n", 20)

    outputs = []
    for (lang, sentiment), group in reviews.groupby(["language", "sentiment"]):
        tokens_iter = tokenize_docs(group["text"], models[lang], allowed_pos, min_token_length)
        counter = count_ngrams(tokens_iter, ngram_size)
        df_top = build_top_ngrams_df(counter, top_n, lang, sentiment)
        outputs.append(df_top)

    top_ngrams = pd.concat(outputs, ignore_index=True) if outputs else pd.DataFrame(
        columns=["language", "sentiment", "ngram", "freq"]
    )

    if write_outputs:
        output_dir = Path(config["output_dir"])
        output_dir.mkdir(exist_ok=True, parents=True)
        good_dir = output_dir / "good"
        bad_dir = output_dir / "bad"
        good_dir.mkdir(exist_ok=True)
        bad_dir.mkdir(exist_ok=True)

        counts.to_csv(output_dir / "summary_counts.csv", index=False)
        top_ngrams.to_csv(output_dir / "top_trigrams_summary.csv", index=False)

        for (lang, sentiment), group in top_ngrams.groupby(["language", "sentiment"]):
            target_dir = good_dir if sentiment == "good" else bad_dir
            filename = f"top_trigrams_{lang}_{sentiment}.csv"
            group.to_csv(target_dir / filename, index=False)

    return {
        "counts": counts,
        "top_ngrams": top_ngrams,
        "reviews": reviews,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Booking Reviews NLP Pipeline")
    parser.add_argument("--config", default="config/config.json", help="Path to config.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    run_pipeline(config, write_outputs=True)


if __name__ == "__main__":
    main()
