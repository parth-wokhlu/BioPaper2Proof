from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


TPTP_PATH = Path("logic/cml_imatinib.p")
OUTPUT_PATH = Path("logic/vampire_output.txt")


def find_vampire_executable() -> str | None:
    """
    Look for a Vampire executable on PATH.
    """
    return shutil.which("vampire")


def run_vampire(problem_path: Path, timeout_seconds: int = 10) -> subprocess.CompletedProcess[str]:
    """
    Run Vampire on a TPTP problem file and capture the output.
    """
    vampire_exe = find_vampire_executable()
    if vampire_exe is None:
        raise FileNotFoundError(
            "Could not find 'vampire' on your PATH. "
            "Install Vampire and make sure the executable is available."
        )

    if not problem_path.exists():
        raise FileNotFoundError(f"TPTP file not found: {problem_path}")

    cmd = [
        vampire_exe,
        str(problem_path),
        "--time_limit",
        str(timeout_seconds),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result


def summarize_result(output: str) -> str:
    """
    Extract a simple status summary from Vampire output.
    """
    output_lower = output.lower()

    if "szs status theorem" in output_lower:
        return "Theorem proved."
    if "szs status countersatisfiable" in output_lower:
        return "Counterexample / countersatisfiable."
    if "szs status satisfiable" in output_lower:
        return "Satisfiable: conjecture not proved."
    if "szs status timeout" in output_lower:
        return "Timed out."
    if "szs status" in output_lower:
        return "Finished with an SZS status."
    return "No recognizable SZS status found."


def save_output(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    try:
        result = run_vampire(TPTP_PATH, timeout_seconds=10)
    except FileNotFoundError as e:
        print(e)
        return

    combined_output = ""
    if result.stdout:
        combined_output += result.stdout
    if result.stderr:
        combined_output += "\n[stderr]\n" + result.stderr

    save_output(combined_output, OUTPUT_PATH)

    print(summarize_result(combined_output))
    print(f"Exit code: {result.returncode}")
    print(f"Saved raw output to {OUTPUT_PATH}")

    print("\n--- Vampire output ---\n")
    print(combined_output)


if __name__ == "__main__":
    main()