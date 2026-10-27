# selfschool-courses

Course packages for Selfschool, a personal, AI-native course platform. Each folder is one course: plain files (lessons, quizzes, exams, sources, runnable lab files) that the app reads directly.

| Course | Level | Length |
|---|---|---|
| `how-llms-work-from-zero-to-your-own-2iy8t7` | Engineer new to ML | about 13 h, 13 chapters, 65 lessons, Python labs |
| `mlops-from-zero-to-production-gblt3l` | Beginner to practitioner | 52 lessons, hands-on labs |
| `rust-from-zero-to-hero-ti89lo` | C/C++ programmer new to Rust | about 12 h, 14 chapters, 38 lessons, 5 Cargo labs and a capstone |
| `typescript-fundamentals` | Beginner | 12 short lessons, plus a demo of every question type |

## Use a course

In Selfschool, open Settings → Course packages and add this repo with the course folder as the path, pinned to a commit. Or clone the repo into the app's `courses/` folder and the app lists every course in it.

Check a course on its own with `school validate <folder>`.

## Layout

```
<course-id>/
  course.yaml        manifest: chapters, exams, level
  sources.md         numbered sources with how much of each was read
  01-chapter/        lesson-NN.md + quiz-NN.yaml per lesson
  exams/             exam blueprints
  resources/         runnable lab files (Python, YAML) linked from the lessons
```

Course ids never change after publishing.

## Licence

Course text is released under [CC BY 4.0](LICENSE): reuse and adapt with credit. The sources each course cites keep their own licences, and short quotes from them stay with their authors.
