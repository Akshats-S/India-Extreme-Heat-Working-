# Builds and checks the preliminary and final submission ZIP files.
"""Build and verify separate preliminary/final self-contained submission ZIPs.

Runs the bundled commands from fresh staging/extracted copies. Never changes
the raw inputs, uploads a submission, or modifies the private submission repo.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_DOCS = ["preparation.md", "methodology.md", "source-metadata.md", "data-dictionary.md",
             "heat-output-schema.md", "research-questions.md", "review-guide.md", "verification-log.md",
             "assignment-checklist.md", "analysis-guide.md", "topic-outline.md", "handout/Instructions.pdf"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def payload_files(directory):
    return sorted(p for p in directory.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def generated_hashes(directory):
    result = {}
    for relative in ("data/processed", "outputs/analysis", "outputs/figures"):
        folder = directory / relative
        if folder.exists():
            result.update({p.relative_to(directory).as_posix(): digest(p) for p in payload_files(folder) if p.name != ".gitkeep"})
    return result


def write_manifest(directory):
    values = {p.relative_to(directory).as_posix(): digest(p) for p in payload_files(directory) if p.name != "MANIFEST.json"}
    (directory / "MANIFEST.json").write_text(json.dumps({"algorithm": "sha256", "files": values}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_manifest(directory):
    manifest = json.loads((directory / "MANIFEST.json").read_text())
    for name, expected in manifest["files"].items():
        path = directory / name
        if not path.resolve().is_relative_to(directory.resolve()):
            raise ValueError("Manifest path escapes the package: " + name)
        if digest(path) != expected:
            raise ValueError("Package fingerprint mismatch: " + name)
    actual = {p.relative_to(directory).as_posix() for p in payload_files(directory) if p.name != "MANIFEST.json"}
    if actual != set(manifest["files"]):
        raise ValueError("Package file list disagrees with the manifest.")
    return len(actual)


def write_archive(directory, path):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in payload_files(directory):
            name = (Path(directory.name) / file.relative_to(directory)).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 31, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, file.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive CRC verification failed.")


def extract_checked(archive_path, destination):
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            if not (destination / name).resolve().is_relative_to(destination.resolve()):
                raise ValueError("ZIP member escapes the extraction directory.")
        archive.extractall(destination)
    roots = list(destination.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError("Archive must contain one package folder.")
    return roots[0]


def run(python, directory, arguments):
    result = subprocess.run([str(python), "-W", "error", *arguments], cwd=directory,
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Command failed: " + " ".join(arguments) + "\n" + result.stdout + result.stderr)
    return result


def copy_sources(staging, mode):
    if mode == "preliminary":
        selected = [ROOT / name for name in
                    ("src/prepare_data.py", "config/cities.geojson", "config/preparation.json")]
    else:
        selected = [ROOT / "requirements.txt", ROOT / "requirements-preliminary.txt", ROOT / "data/README.md"]
        for pattern in ("src/*.py", "tests/test_*.py", "config/*.json", "config/*.geojson", "docs/package-templates/*.txt"):
            selected.extend(ROOT.glob(pattern))
        selected.extend(ROOT / "docs" / name for name in CORE_DOCS)
    selected.extend((ROOT / "data/raw").glob("*.csv"))
    for source in selected:
        if not source.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Source path is outside the project.")
        destination = staging / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    if mode == "preliminary":
        shutil.copy2(ROOT / "requirements-preliminary.txt", staging / "requirements.txt")
    metadata = json.loads((ROOT / "config/submission.json").read_text())
    members = metadata["team_members"]
    if not isinstance(members, list) or any(not isinstance(name, str) or not name.strip() for name in members):
        raise ValueError("team_members must be a list of nonempty names.")
    names = "; ".join(members) if members else "ADD TEAM MEMBER NAMES BEFORE SUBMISSION"
    section = metadata["course_section"]
    template = (ROOT / f"docs/package-templates/README-{mode}.txt").read_text(encoding="utf-8")
    if not section:
        template = template.replace("Section: {{SECTION}}\n", "")
    for field, value in (("COURSE", metadata["course"]), ("YEAR", metadata["academic_year"]), ("TEAM", names), ("SECTION", section)):
        template = template.replace("{{" + field + "}}", value)
    (staging / "README.md").write_text(template, encoding="utf-8")
    if mode == "final":
        (staging / "COVER.md").write_text(
            f"# India extreme heat - {mode} assessment\n\nCourse: {metadata['course']} ({metadata['academic_year']})\n\n"
            f"Team: {names}\n\n"
            + (f"Section: {section}\n\n" if section else "")
            + f"Deadline: {metadata[mode + '_deadline']}\n",
            encoding="utf-8")
    if mode == "final":
        shutil.copy2(ROOT / "docs/topic-outline.md", staging / "TOPIC_OUTLINE.md")
        shutil.copy2(ROOT / "docs/research-questions.md", staging / "RESEARCH_QUESTIONS.md")
    return bool(members)


def build_package(mode, output_dir, python):
    deadline = "2026-11-06" if mode == "preliminary" else "2026-11-30"
    name = f"india-extreme-heat-{mode}-{deadline}"
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="heat-submission-build-") as temporary:
        base = Path(temporary).resolve()
        staging = base / name
        staging.mkdir()
        names_complete = copy_sources(staging, mode)
        raw_before = {p.name: digest(p) for p in (staging / "data/raw").glob("*.csv")}
        command = ["src/prepare_data.py", "--skip-heat"] if mode == "preliminary" else ["src/run_project.py"]
        print(f"{mode}: generating a fresh package...", flush=True)
        run(python, staging, command)
        first = generated_hashes(staging)
        run(python, staging, command)
        if first != generated_hashes(staging):
            raise ValueError(mode + ": repeated regeneration changed output bytes.")
        print(f"{mode}: repeated outputs match; running all tests...", flush=True)
        # Development tests stay outside the deliberately minimal preliminary hand-in.
        test_directory = ROOT if mode == "preliminary" else staging
        tests = run(python, test_directory, ["-m", "unittest", "discover", "-s", "tests", "-v"])
        match = re.search(r"Ran (\d+) tests?", tests.stderr)
        if not match:
            raise ValueError("Unable to establish the executed test count.")
        if raw_before != {p.name: digest(p) for p in (staging / "data/raw").glob("*.csv")}:
            raise ValueError("Raw inputs changed during package verification.")
        checks = {"status": "passed", "mode": mode, "tests_run": int(match.group(1)),
                  "tests_return_code": 0, "repeated_output_hashes_match": True,
                  "raw_inputs_unchanged": True, "team_names_present": names_complete,
                  "source_file_fingerprints": "MANIFEST.json", "regeneration_command": "python " + " ".join(command),
                  "generated_files_sha256": first}
        archive_path = base / (name + ".zip")
        if mode == "preliminary":
            # Ship the requested dataset, code and outline plus runtime inputs only.
            for file in (staging / "data/processed").iterdir():
                if file.name != "daily_temperatures.csv":
                    file.unlink()
            approved = {p.relative_to(staging).as_posix(): digest(p) for p in payload_files(staging)}
            checks["package_files_sha256"] = approved
            checks["source_file_fingerprints"] = "package_build_report.json (outside the hand-in)"
            write_archive(staging, archive_path)
            extracted = extract_checked(archive_path, base / "extracted")
            actual = {p.relative_to(extracted).as_posix(): digest(p) for p in payload_files(extracted)}
            if actual != approved:
                raise ValueError("Preliminary ZIP does not match its approved file list.")
            print(f"{mode}: regenerating from the extracted ZIP...", flush=True)
            run(python, extracted, command)
            if first != generated_hashes(extracted):
                raise ValueError("Extracted preliminary ZIP did not regenerate the verified outputs.")
            if any(digest(extracted / relative) != expected for relative, expected in approved.items()):
                raise ValueError("Preliminary reproduction changed a bundled input or dataset.")
            checks["zip_extraction_reproduction_passed"] = True
            included = len(approved)
        else:
            check_path = staging / "PACKAGE_CHECKS.json"
            check_path.write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            write_manifest(staging)
            write_archive(staging, archive_path)
            extracted = extract_checked(archive_path, base / "extracted")
            verify_manifest(extracted)
            print(f"{mode}: regenerating from the extracted ZIP...", flush=True)
            run(python, extracted, command)
            if first != generated_hashes(extracted):
                raise ValueError("Extracted ZIP did not reproduce its included outputs.")
            verify_manifest(extracted)
            checks["zip_extraction_reproduction_passed"] = True
            check_path.write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            write_manifest(staging)
            write_archive(staging, archive_path)
            final_extract = extract_checked(archive_path, base / "final-extracted")
            included = verify_manifest(final_extract) + 1
            if first != generated_hashes(final_extract):
                raise ValueError("Final archive's verified data payload changed.")
        destination = output_dir / (name + ".zip")
        handle, temporary_zip = tempfile.mkstemp(dir=output_dir, suffix=".zip.tmp")
        os.close(handle)
        try:
            shutil.copyfile(archive_path, temporary_zip)
            os.replace(temporary_zip, destination)
        finally:
            if os.path.exists(temporary_zip):
                os.unlink(temporary_zip)
        return {"archive": destination.name, "sha256": digest(destination), "bytes": destination.stat().st_size,
                "included_files": included, **checks}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT.parent / "Submissions")
    parser.add_argument("--verify-python", type=Path, default=Path(sys.executable), help="Python with requirements installed, optionally from a fresh virtual environment.")
    parser.add_argument("--mode", choices=("both", "preliminary", "final"), default="both")
    args = parser.parse_args(argv)
    raw = (ROOT / "data/raw").resolve()
    if args.output_dir.resolve() == raw or raw in args.output_dir.resolve().parents:
        parser.error("Packages must not be written into the raw-data directory.")
    try:
        modes = ("preliminary", "final") if args.mode == "both" else (args.mode,)
        results = {mode: build_package(mode, args.output_dir.resolve(), args.verify_python.resolve()) for mode in modes}
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "package_build_report.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        print("Package verification failed: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps({mode: {key: value for key, value in result.items() if key != "generated_files_sha256"} for mode, result in results.items()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
