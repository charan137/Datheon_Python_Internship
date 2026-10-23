"""Organize files in a directory into extension-based category folders."""

import argparse
import os
import shutil
from pathlib import Path

EXTENSION_CATEGORIES = {
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".odt": "Documents",
    ".rtf": "Documents",
    ".txt": "Documents",
    ".md": "Documents",
    ".csv": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".heic": "Images",
    ".mp4": "Videos",
    ".mov": "Videos",
    ".avi": "Videos",
    ".mkv": "Videos",
    ".wmv": "Videos",
    ".webm": "Videos",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".aac": "Audio",
    ".m4a": "Audio",
    ".flac": "Audio",
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".bz2": "Archives",
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".html": "Code",
    ".css": "Code",
    ".java": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".h": "Code",
    ".cs": "Code",
    ".go": "Code",
    ".rs": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".sql": "Code",
    ".sh": "Code",
}
CATEGORY_DIRECTORIES = frozenset((*EXTENSION_CATEGORIES.values(), "Others"))


def category_for(filename):
    """Return the category for a filename, or Others for unknown extensions."""
    return EXTENSION_CATEGORIES.get(Path(filename).suffix.lower(), "Others")


def available_destination(directory, filename, reserved=None):
    """Choose a destination path that does not already exist."""
    destination = directory / filename
    if not destination.exists() and destination not in (reserved or set()):
        return destination

    original = Path(filename)
    counter = 1
    while True:
        candidate = directory / f"{original.stem} ({counter}){original.suffix}"
        if not candidate.exists() and candidate not in (reserved or set()):
            return candidate
        counter += 1


def iter_files(source_directory, recursive, result):
    """Yield regular files and record entries that cannot be inspected."""
    pending_directories = [source_directory]
    while pending_directories:
        current_directory = pending_directories.pop()
        try:
            with os.scandir(current_directory) as scanned_entries:
                entries = sorted(scanned_entries, key=lambda item: item.name.lower())
        except OSError as error:
            result["failed"].append((str(current_directory), str(error)))
            continue

        for entry in entries:
            relative_path = Path(entry.path).relative_to(source_directory)
            try:
                if entry.is_file(follow_symlinks=False):
                    yield Path(entry.path)
                elif (
                    recursive
                    and entry.is_dir(follow_symlinks=False)
                    and entry.name not in CATEGORY_DIRECTORIES
                ):
                    pending_directories.append(Path(entry.path))
            except OSError as error:
                result["failed"].append((str(relative_path), str(error)))


def organize_directory(directory, apply_changes=False, recursive=False):
    """Plan or perform organization of regular files in a directory."""
    source_directory = Path(directory).expanduser().resolve()
    if not source_directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {source_directory}")
    if not source_directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {source_directory}")

    result = {"scanned": 0, "planned": [], "moved": [], "skipped": [], "failed": []}

    reserved_destinations = set()
    for source_path in iter_files(source_directory, recursive, result):
        relative_path = source_path.relative_to(source_directory)
        display_name = str(relative_path)
        result["scanned"] += 1
        category_directory = source_directory / category_for(source_path.name)
        destination = available_destination(
            category_directory, source_path.name, reserved_destinations
        )

        if not apply_changes:
            result["planned"].append((display_name, destination))
            reserved_destinations.add(destination)
            continue

        try:
            category_directory.mkdir(exist_ok=True)
            destination = available_destination(
                category_directory, source_path.name, reserved_destinations
            )
            shutil.move(str(source_path), str(destination))
            result["moved"].append((display_name, destination))
            reserved_destinations.add(destination)
        except (PermissionError, FileExistsError, OSError) as error:
            result["failed"].append((display_name, str(error)))

    return result


def display_summary(result, apply_changes):
    mode = "APPLY" if apply_changes else "DRY RUN"
    print(f"\nFile organizer: {mode}")

    entries = result["moved"] if apply_changes else result["planned"]
    label = "Moved" if apply_changes else "Would move"
    for filename, destination in entries:
        print(f"{label:<10} {filename} -> {destination.parent.name}/{destination.name}")

    for filename, reason in result["skipped"]:
        print(f"Skipped    {filename}: {reason}")
    for filename, reason in result["failed"]:
        print(f"Failed     {filename}: {reason}")

    print("\nExecution summary")
    print(f"  Files inspected: {result['scanned']}")
    print(f"  Files relocated: {len(result['moved'])}")
    print(f"  Files planned:   {len(result['planned'])}")
    print(f"  Files skipped:   {len(result['skipped'])}")
    print(f"  Files failed:    {len(result['failed'])}")
    if not apply_changes:
        print("  No files were changed. Re-run with --apply to move them.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        nargs="?",
        default=str(Path.home() / "Downloads"),
        help="directory to organize (default: ~/Downloads)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the moves (default is a non-destructive dry run)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="also organize files in subdirectories, leaving category folders alone",
    )
    args = parser.parse_args()

    try:
        result = organize_directory(
            args.directory,
            apply_changes=args.apply,
            recursive=args.recursive,
        )
    except (OSError, PermissionError) as error:
        parser.error(str(error))
    display_summary(result, args.apply)
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())