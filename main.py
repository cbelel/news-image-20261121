"""Deliver the bundled image and verify that the copy preserves its bytes."""
import os
from pathlib import Path
import shutil


def main():
    source = Path(__file__).resolve().with_name("entry.png")
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / source.name
    expected = source.read_bytes()
    if not destination.exists() or not source.samefile(destination):
        shutil.copyfile(source, destination)
    if destination.read_bytes() != expected:
        raise OSError(f"Image copy did not preserve the bytes: {destination}")


if __name__ == "__main__":
    main()
