import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


FRAME_KEYWORDS = {
    "карьера и лидерство": [
        "карьер", "лидер", "руковод", "бизнес", "предприним",
        "проект", "директор", "професси", "команд", "инвест"
    ],
    "барьеры и неравенство": [
        "барьер", "неравен", "стереотип", "трудност", "потолок",
        "дискриминац", "предвзя", "мешает", "двойная нагрузка"
    ],
    "самореализация и выбор": [
        "самореал", "выбор", "свобод", "себя", "траектор",
        "перемены", "поиск", "личный", "развитие"
    ],
    "баланс семьи и работы": [
        "семь", "дет", "материн", "мама", "дом", "родител",
        "баланс", "отношен", "партнер", "быт"
    ],
    "статус и публичность": [
        "статус", "публич", "рейтинг", "признан", "известн",
        "репутац", "медиа", "популяр", "список", "forbes"
    ],
}


def clean_text(text: str) -> str:
    text = str(text).lower().replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def classify_frame(text: str) -> str:
    text = clean_text(text)
    scores = {}

    for frame, keywords in FRAME_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        scores[frame] = score

    best_frame = max(scores, key=scores.get)

    if scores[best_frame] == 0:
        return "не определено"

    return best_frame


def main():
    input_file = Path("successful_woman_articles_final.csv")
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    df = pd.read_csv(input_file)

    required_columns = {"platform", "media_type", "title", "lead"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"В таблице не хватает колонок: {missing}")

    df["title"] = df["title"].fillna("").astype(str)
    df["lead"] = df["lead"].fillna("").astype(str)
    df["text_for_analysis"] = df["title"] + " " + df["lead"]

    df["frame"] = df["text_for_analysis"].apply(classify_frame)

    df.to_csv(output_dir / "corpus_with_frames.csv", index=False, encoding="utf-8-sig")

    # График 1 — общий корпус
    frame_counts = df["frame"].value_counts()

    plt.figure(figsize=(10, 6))
    frame_counts.plot(kind="barh")
    plt.title("Фреймы образа успешной женщины: общий корпус")
    plt.xlabel("Количество публикаций")
    plt.ylabel("Фрейм")
    plt.tight_layout()
    plt.savefig(output_dir / "frame_counts_overall.png", dpi=300)
    plt.show()

    # График 2 — сравнение типов медиа
    media_frame_counts = pd.crosstab(df["media_type"], df["frame"])

    media_frame_counts.plot(kind="bar", figsize=(11, 6))
    plt.title("Сравнение фреймов в деловых и лайфстайл-медиа")
    plt.xlabel("Тип медиа")
    plt.ylabel("Количество публикаций")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "frame_counts_by_media_type.png", dpi=300)
    plt.show()

    # График 3 — проценты по типам медиа
    media_frame_percent = pd.crosstab(
        df["media_type"],
        df["frame"],
        normalize="index"
    ) * 100

    media_frame_percent.plot(kind="bar", stacked=True, figsize=(11, 6))
    plt.title("Доли фреймов по типам медиа, %")
    plt.xlabel("Тип медиа")
    plt.ylabel("Доля публикаций, %")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "frame_percent_by_media_type.png", dpi=300)
    plt.show()

    # Сохранение таблиц
    frame_counts.to_csv(output_dir / "frame_counts_overall.csv", encoding="utf-8-sig")
    media_frame_counts.to_csv(output_dir / "frame_counts_by_media_type.csv", encoding="utf-8-sig")
    media_frame_percent.to_csv(output_dir / "frame_percent_by_media_type.csv", encoding="utf-8-sig")

    print("Анализ завершён.")
    print(f"Всего публикаций: {len(df)}")
    print("Результаты сохранены в папку results")


if __name__ == "__main__":
    main()