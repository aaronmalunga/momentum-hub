import argparse
import os
import re

LOCAL_MODULES = {
    "category",
    "goal",
    "habit",
    "completion",
    "encouragements",
    "error_manager",
    "momentum_utils",
    "seed_data",
    "cli_analysis",
    "cli_category_management",
    "cli_display",
    "cli_export",
    "cli_goal_management",
    "cli_habit_management",
    "cli_utils",
    "momentum_cli",
    "momentum_main",
    "momentum_db",
}


def _iter_py_files(root_dir: str):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)


def fix_stdlib_relative_imports(package_dir: str) -> None:
    """
    Fix accidental relative imports of stdlib/third-party modules.
    Example: `from .os import path` -> `from os import path`.
    """
    for file_path in _iter_py_files(package_dir):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        fixed_lines = []
        for line in lines:
            match = re.match(r"from \.(\w+) import", line)
            if match:
                module = match.group(1)
                if module not in LOCAL_MODULES:
                    line = re.sub(r"from \.(\w+) import \*", r"import \1", line)
                    line = re.sub(
                        r"from \.(\w+) import (.+)", r"from \1 import \2", line
                    )
            fixed_lines.append(line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)


def make_local_imports_relative(package_dir: str) -> None:
    """
    Convert absolute local imports to relative imports within the package.
    Example: `from habit import Habit` -> `from .habit import Habit`.
    """
    pattern = r"from (" + "|".join(sorted(LOCAL_MODULES)) + r") import"
    for file_path in _iter_py_files(package_dir):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(pattern, r"from .\1 import", content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def convert_imports_to_relative(package_dir: str) -> None:
    """
    Convert `import module` for local modules to relative imports.
    Example: `import habit` -> `from . import habit`.
    """
    module_group = "|".join(sorted(LOCAL_MODULES))
    for file_path in _iter_py_files(package_dir):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            rf"^import ({module_group}) as (\w+)",
            r"from . import \1 as \2",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            rf"^import ({module_group})$",
            r"from . import \1",
            content,
            flags=re.MULTILINE,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def update_test_imports(tests_dir: str) -> None:
    """
    Update test imports to use the package namespace (momentum_hub.*).
    """
    for file_path in _iter_py_files(tests_dir):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            r"^import momentum_db",
            "import momentum_hub.momentum_db",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^from momentum_db",
            "from momentum_hub.momentum_db",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^from category import",
            "from momentum_hub.category import",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^from goal import",
            "from momentum_hub.goal import",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^from habit import",
            "from momentum_hub.habit import",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^from seed_data import",
            "from momentum_hub.seed_data import",
            content,
            flags=re.MULTILINE,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import refactor utilities for Momentum Hub."
    )
    parser.add_argument(
        "--package-dir",
        default="momentum_hub",
        help="Package directory to update (default: momentum_hub)",
    )
    parser.add_argument(
        "--tests-dir",
        default="tests",
        help="Tests directory to update (default: tests)",
    )
    parser.add_argument(
        "--fix-stdlib-relative",
        action="store_true",
        help="Fix accidental relative imports of stdlib/third-party modules.",
    )
    parser.add_argument(
        "--make-relative",
        action="store_true",
        help="Convert absolute local imports to relative imports.",
    )
    parser.add_argument(
        "--convert-imports",
        action="store_true",
        help="Convert local `import module` to `from . import module`.",
    )
    parser.add_argument(
        "--update-tests",
        action="store_true",
        help="Update tests to import via momentum_hub.* namespace.",
    )
    args = parser.parse_args()

    if args.fix_stdlib_relative:
        fix_stdlib_relative_imports(args.package_dir)
    if args.make_relative:
        make_local_imports_relative(args.package_dir)
    if args.convert_imports:
        convert_imports_to_relative(args.package_dir)
    if args.update_tests:
        update_test_imports(args.tests_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
