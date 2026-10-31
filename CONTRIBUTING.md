# Maintaining the completed project

Make corrections in this working repository, then rebuild the assessment
packages and update the submission copies. Each assessment remains independently
reproducible.

1. Update local `main` and create a focused branch.
2. Preserve raw inputs; change source, settings or documentation as needed.
3. Run checks appropriate to the change. For pipeline/package changes, run
   `python -W error -m unittest discover -s tests -v` and rebuild the packages.
4. Open a pull request describing the change and validation. Integrate through
   the PR; direct pushes to `main` are prohibited. No separate teammate
   approval is required for lead-owned work.
5. Copy verified packages to the preliminary/final submission folders as
   appropriate. Preserve the exact version actually submitted to the course.

Keep source citations, measurement limitations and execution records accurate.
Automated tests do not imply human sign-off. Never commit credentials, local
environments or tool authorship/co-authorship footers.
