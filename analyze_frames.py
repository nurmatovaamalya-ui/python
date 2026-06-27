from __future__ import annotations

import argparse
import re
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd
import matplotlib.pyplot as plt

FRAME_KEYWORDS = {
    "карьера и лидерство": ["карьер", "лидер", "руковод", "бизнес", "предприним", "проект", "повышен", "должност", "професси", "команд", "инвест", "капитал", "цели", "рост"],
    "барьеры и неравенство": ["барьер", "мешает", "трудност", "неравен", "стереотип", "самозван", "потолок", "тревог", "недовер", "доказывать", "двойная нагруз", "критик", "предвзя"],
    "самореализация и выбор": ["самореал", "любимым делом", "выбор", "себя", "свобод", "пауза", "любим", "траектор", "сохранить себя", "поиск", "перемены"],
    "баланс и семья": ["семь", "муж", "замуж", "дет", "материн", "дом", "партнер", "отношен", "родител", "быт", "баланс"],
    "статус и публичность": ["рейтинг", "статус", "публич", "признан", "репутац", "известн", "популяр", "медиа", "кино", "список forbes"],
}

STOPWORDS = {"и", "в", "на", "с", "о", "об", "к", "по", "для", "как", "что", "это", "или", "при", "до", "за", "из", "не", "женщин", "женщина", "женщины", "успех", "успешных", "успешная", "карьера", "карьере", "карьеру"}


def classify_frame(text: str) -> tuple[str, str]:
    t = str(text).lower().replace("ё", "е")
    scores = {frame: 0 for frame in FRAME_KEYWORDS}
    found = []
    for frame, keywords in FRAME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in t:
                scores[frame] += 1
                found.append(keyword)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "самореализация и выбор", ""
    return best, "; ".join(sorted(set(found))[:8])


def load_corpus(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"id", "platform", "date", "title", "url", "context"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Не хватает столбцов: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["platform", "title", "context"]).drop_duplicates(subset=["platform", "title"]).copy()
    return df


def add_auto_frames(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    predictions = df.apply(lambda r: classify_frame(f"{r['title']} {r['context']}"), axis=1)
    df["frame_auto"] = [x[0] for x in predictions]
    df["markers"] = [x[1] for x in predictions]
    if "frame_manual" in df.columns:
        df["match_manual_auto"] = df["frame_manual"] == df["frame_auto"]
    else:
        df["frame_manual"] = df["frame_auto"]
        df["match_manual_auto"] = True
    return df


def make_tables(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "corpus_with_frames.csv", index=False, encoding="utf-8-sig")
    counts = df["frame_manual"].value_counts().rename_axis("frame").reset_index(name="count")
    counts.to_csv(out_dir / "frame_counts_overall.csv", index=False, encoding="utf-8-sig")
    by_platform = pd.crosstab(df["platform"], df["frame_manual"]).reset_index()
    by_platform.to_csv(out_dir / "frame_counts_by_platform.csv", index=False, encoding="utf-8-sig")
    percent = (pd.crosstab(df["platform"], df["frame_manual"], normalize="index") * 100).round(1).reset_index()
    percent.to_csv(out_dir / "frame_percent_by_platform.csv", index=False, encoding="utf-8-sig")
    df.groupby("frame_manual").head(3)[["platform", "date", "title", "frame_manual", "url"]].to_csv(out_dir / "frame_examples.csv", index=False, encoding="utf-8-sig")
    if "match_manual_auto" in df.columns:
        pd.DataFrame([{"metric": "manual_auto_agreement", "value": round(df["match_manual_auto"].mean() * 100, 1)}]).to_csv(out_dir / "classification_check.csv", index=False, encoding="utf-8-sig")


def top_words(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for frame, group in df.groupby("frame_manual"):
        counter = Counter()
        for text in (group["title"] + " " + group["context"]):
            counter.update(w for w in re.findall(r"[а-яёa-z\-]{4,}", text.lower()) if w not in STOPWORDS)
        for word, count in counter.most_common(8):
            rows.append({"frame": frame, "word": word, "count": count})
    return pd.DataFrame(rows)


def make_charts(df: pd.DataFrame, out_dir: Path) -> None:
    plt.rcParams["font.family"] = "DejaVu Sans"
    counts = df["frame_manual"].value_counts().rename_axis("frame").reset_index(name="count")
    order = counts.sort_values("count", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh(order["frame"], order["count"])
    ax.set_title("Фреймы образа успешной женщины: общий корпус")
    ax.set_xlabel("Количество материалов")
    for i, v in enumerate(order["count"]):
        ax.text(v + 0.2, i, str(v), va="center")
    fig.tight_layout()
    fig.savefig(out_dir / "frame_counts_overall.png", dpi=220)
    plt.close(fig)

    percent = (pd.crosstab(df["platform"], df["frame_manual"], normalize="index") * 100).round(1)
    fig, ax = plt.subplots(figsize=(10, 5.4))
    percent.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Доли фреймов по платформам, %")
    ax.set_ylabel("Доля материалов, %")
    ax.set_xlabel("Платформа")
    ax.legend(title="Фрейм", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    fig.tight_layout()
    fig.savefig(out_dir / "frame_percent_by_platform.png", dpi=220)
    plt.close(fig)

    by_platform = pd.crosstab(df["platform"], df["frame_manual"])
    fig, ax = plt.subplots(figsize=(10, 5.4))
    by_platform.plot(kind="bar", ax=ax)
    ax.set_title("Фреймы по платформам: абсолютные значения")
    ax.set_ylabel("Количество материалов")
    ax.set_xlabel("Платформа")
    ax.legend(title="Фрейм", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    fig.tight_layout()
    fig.savefig(out_dir / "frame_counts_by_platform.png", dpi=220)
    plt.close(fig)

    words = top_words(df)
    words.to_csv(out_dir / "frame_marker_words.csv", index=False, encoding="utf-8-sig")
    top = words.groupby("frame").head(3)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    labels = [f"{r['frame']}: {r['word']}" for _, r in top.iterrows()]
    ax.barh(range(len(top)), top["count"])
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels)
    ax.set_title("Частотные слова-маркеры по фреймам")
    ax.set_xlabel("Частота")
    fig.tight_layout()
    fig.savefig(out_dir / "frame_marker_words.png", dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=Path(__file__).with_name("successful_woman_articles.csv"))
    parser.add_argument("--out", default=Path(__file__).with_name("results"))
    args = parser.parse_args()
    out_dir = Path(args.out)
    df = load_corpus(Path(args.input))
    df = add_auto_frames(df)
    make_tables(df, out_dir)
    make_charts(df, out_dir)
    summary = [
        f"Всего материалов: {len(df)}",
        "Платформы: " + ", ".join(df["platform"].value_counts().index.tolist()),
        "",
        "Распределение фреймов:",
        df["frame_manual"].value_counts().to_string(),
    ]
    (out_dir / "summary.txt").write_text("\n".join(summary), encoding="utf-8")
    print("Всего материалов:", len(df))
    print("Результаты сохранены в:", out_dir.resolve())


if __name__ == "__main__":
    main()
