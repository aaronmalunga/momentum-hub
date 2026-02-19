# Submission Checklist (OOFPP Habit Tracker Portfolio)

This checklist tracks rubric compliance and lecturer feedback. Mark items done when verified in the repo or in the final PebblePad submission.

**Portfolio Phases (PebblePad)**
1. [ ] Phase 1 (Conception): 1-3 page concept PDF with at least one diagram.
2. [ ] Phase 2 (Development/Reflection): 5-10 slide PDF with visuals and implementation explanation.
3. [ ] Phase 3 (Finalization): 1-2 page abstract PDF with GitHub link + final code + zip + resubmitted Phase 1 & 2.

**Evaluation Criteria (Rubric)**
1. [ ] Problem Solving Techniques (10%): clear problem definition + understandable concept.
2. [ ] Methodology/Ideas/Procedure (20%): OOP for habits + functional analytics + rationale for tools.
3. [ ] Quality of Implementation (40%): usable app + clear docs + acceptance criteria met.
4. [ ] Creativity/Correctness (20%): solution meets objectives + unit tests for core features.
5. [ ] Formal Requirements (10%): naming, format, submission steps, GitHub link, zip structure.

**Acceptance Criteria (Technical)**
1. [x] Python 3.7+ compatible. `pyproject.toml`
2. [x] Clear install/run instructions. `README.md`
3. [x] Habit modeled as OOP class. `momentum_hub/habit.py`
4. [x] Daily + weekly habits supported. `momentum_hub/habit.py`, `momentum_hub/momentum_db.py`
5. [x] 5 predefined habits. `tests/test_data.py`, `momentum_hub/seed_data.py`
6. [x] Track creation + completion timestamps. `momentum_hub/momentum_db.py`
7. [x] 4 weeks of predefined completion data for tests. `tests/test_data.py`
8. [x] Data persistence (SQLite). `momentum_hub/momentum_db.py`
9. [x] Analytics module uses functional style for core queries. `momentum_hub/habit_analysis.py`
10. [x] CLI for create/delete/analyze. `momentum_hub/momentum_cli.py`, `momentum_hub/cli_*`
11. [x] Unit tests for core components and analytics. `tests/`

**Lecturer Feedback Checklist**
1. [ ] Add screenshots from functional app to support presentation (use real UI runs).
2. [ ] Add screenshots from results/tests (e.g., `pytest` summary and/or coverage).
3. [x] GitHub repo (code, not zipped) + polished README. `README.md`
4. [x] Unit tests present. `tests/`
5. [x] Naming conventions + ignore unnecessary files. `.gitignore`
6. [x] Modular structure. `momentum_hub/`
7. [x] Basic code comments/docstrings. `momentum_hub/`
8. [x] Analytics module complete per guideline. `momentum_hub/habit_analysis.py`
9. [x] Streak respects periodicity (daily vs weekly). `momentum_hub/momentum_db.py`, `momentum_hub/habit_analysis.py`
10. [x] 4-week fixture data for streak tests. `tests/test_data.py`
11. [x] Unit tests cover habit CRUD + analytics. `tests/test_habit.py`, `tests/test_habit_analysis.py`, `tests/test_pure_analysis.py`
