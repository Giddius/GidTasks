from pathlib import Path


THIS_FILE_DIR = Path(__file__).parent.absolute()


TEMPLATE_FILES: dict[str, Path] = {}

for file in THIS_FILE_DIR.iterdir():
    if file.name == '__init__.py':
        continue
    TEMPLATE_FILES[file.stem] = file
