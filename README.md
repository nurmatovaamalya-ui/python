# Образ успешной женщины в цифровых медиа

Тема: **через какие фреймы в цифровых медиа конструируется образ успешной женщины**.

Платформы: Wonderzine и Forbes Woman.

## Что внутри

- `successful_woman_articles.csv` — корпус материалов.
- `analyze_frames.py` — код анализа.
- `results/` — готовые таблицы и графики.
- `successful_woman_presentation.pptx` — презентация для защиты.
- `requirements.txt` — зависимости.

## Запуск

```bash
python -m pip install -r requirements.txt
python analyze_frames.py
```

## Метод

Метод исследования — контент-анализ и фрейм-анализ заголовков и краткого контекста материалов. Фрейм понимается как рамка, через которую медиа объясняет успех женщины: карьера, барьеры, самореализация, семья/баланс или публичный статус.

Python используется для очистки таблицы, словарной авторазметки фреймов, подсчётов и визуализаций.

## Основные файлы результатов

- `results/frame_counts_overall.csv`
- `results/frame_counts_by_platform.csv`
- `results/frame_percent_by_platform.csv`
- `results/frame_examples.csv`
- `results/corpus_with_frames.csv`
- `results/frame_counts_overall.png`
- `results/frame_percent_by_platform.png`
- `results/frame_marker_words.png`

## Корпус

Всего материалов: 40.

Запросы для отбора: `успешная женщина`, `успешные женщины`, `женская карьера`, `успех`, `самореализация` внутри Wonderzine и Forbes Woman.
