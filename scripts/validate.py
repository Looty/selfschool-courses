"""Check every course package in this repo.

Run from the repo root: python scripts/validate.py
Needs PyYAML. Exits with 1 and lists the problems if any check fails.
"""

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CITE = re.compile(r"\[(\d+)\]")
SOURCE_ENTRY = re.compile(r"^(\d+)\. ", re.M)

errors = []


def error(path, message):
    errors.append(f"{path.relative_to(ROOT).as_posix()}: {message}")


def load_yaml(path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        error(path, f"invalid YAML: {exc}")
        return None


def split_lesson(path):
    """Return (frontmatter dict, body) for a lesson file."""
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if not text.startswith("---") or len(parts) < 3:
        error(path, "missing --- frontmatter")
        return None, ""
    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        error(path, f"invalid frontmatter: {exc}")
        return None, ""
    if not isinstance(meta, dict):
        error(path, "frontmatter is not a mapping")
        return None, ""
    return meta, parts[2]


def prose_citations(body):
    """Citation numbers in the lesson text, ignoring code blocks and inline code."""
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"`[^`\n]*`", "", body)
    return {int(n) for n in CITE.findall(body)}


def check_lessons(course, lesson_files, known_sources, lesson_ids):
    for lesson in lesson_files:
        meta, body = split_lesson(lesson)
        if meta is None:
            continue
        if "id" not in meta:
            error(lesson, "frontmatter has no id")
        else:
            lesson_ids[meta["id"]] += 1
        quiz = meta.get("quiz")
        if quiz and not (lesson.parent / quiz).is_file():
            error(lesson, f"quiz file not found: {quiz}")
        for resource in meta.get("resources") or []:
            if not (lesson.parent / resource).exists():
                error(lesson, f"resource not found: {resource}")
        if known_sources is None:
            continue
        listed = meta.get("sources")
        listed = set(listed) if isinstance(listed, list) else set()  # some lessons say "sources: none"
        for n in sorted(listed - known_sources):
            error(lesson, f"frontmatter source [{n}] is not in sources.md")
        for n in sorted(prose_citations(body) - known_sources):
            error(lesson, f"cites [{n}], which is not in sources.md")


def check_quizzes(quiz_files, known_sources, quiz_ids, question_ids):
    for quiz in quiz_files:
        data = load_yaml(quiz)
        if not isinstance(data, dict):
            if data is not None:
                error(quiz, "not a mapping")
            continue
        if "id" in data:
            quiz_ids[data["id"]] += 1
        for question in data.get("questions") or []:
            if not isinstance(question, dict):
                continue
            if "id" in question:
                question_ids[question["id"]] += 1
            if known_sources is None:
                continue
            for n in question.get("sources") or []:
                if n not in known_sources:
                    error(quiz, f"question {question.get('id')} cites [{n}], which is not in sources.md")


def report_duplicates(path, kind, counter):
    for key, count in counter.items():
        if count > 1:
            error(path, f"{kind} id {key!r} is used {count} times")


def check_course(course):
    manifest = course / "course.yaml"
    data = load_yaml(manifest)
    if not isinstance(data, dict):
        return
    if data.get("id") != course.name:
        error(manifest, f"id {data.get('id')!r} does not match the folder name")

    sources_file = course / "sources.md"
    known_sources = None
    if sources_file.is_file():
        known_sources = {int(n) for n in SOURCE_ENTRY.findall(sources_file.read_text(encoding="utf-8"))}

    lesson_files, quiz_files = [], []
    for chapter in data.get("chapters") or []:
        chapter_dir = course / chapter.get("dir", "")
        if not chapter_dir.is_dir():
            error(manifest, f"chapter folder not found: {chapter.get('dir')}")
            continue
        lesson_files += sorted(chapter_dir.glob("lesson-*.md"))
        quiz_files += sorted(chapter_dir.glob("quiz-*.yaml"))

    for exam in data.get("exams") or []:
        exam_file = course / exam.get("file", "")
        if exam_file.is_file():
            quiz_files.append(exam_file)
        else:
            error(manifest, f"exam file not found: {exam.get('file')}")

    lesson_ids, quiz_ids, question_ids = Counter(), Counter(), Counter()
    check_lessons(course, lesson_files, known_sources, lesson_ids)
    check_quizzes(quiz_files, known_sources, quiz_ids, question_ids)
    report_duplicates(manifest, "lesson", lesson_ids)
    report_duplicates(manifest, "quiz", quiz_ids)
    report_duplicates(manifest, "question", question_ids)

    # Translations only need to parse; their ids mirror the original course.
    for path in sorted((course / "i18n").rglob("*")) if (course / "i18n").is_dir() else []:
        if path.suffix == ".yaml":
            load_yaml(path)
        elif path.name.startswith("lesson-") and path.suffix == ".md":
            split_lesson(path)


def main():
    courses = sorted(p.parent for p in ROOT.glob("*/course.yaml"))
    if not courses:
        print("No courses found.")
        return 1
    for course in courses:
        check_course(course)
    if errors:
        print(f"{len(errors)} problem(s):")
        for line in errors:
            print(f"  {line}")
        return 1
    print(f"Checked {len(courses)} course(s): all good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
