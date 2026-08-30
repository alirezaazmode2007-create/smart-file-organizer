"""
Pytest configuration and fixtures for Smart File Organizer tests.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_categories():
    """Sample categories for testing."""
    return {
        "images": {
            "extensions": [".jpg", ".jpeg", ".png", ".gif"],
            "folder_name": "Images",
            "icon": "🖼️"
        },
        "documents": {
            "extensions": [".pdf", ".doc", ".docx", ".txt"],
            "folder_name": "Documents",
            "icon": "📄"
        },
        "code": {
            "extensions": [".py", ".js", ".html", ".css"],
            "folder_name": "Code",
            "icon": "💻"
        }
    }


@pytest.fixture
def categories_file(temp_dir, sample_categories):
    """Create a temporary categories.json file."""
    categories_path = temp_dir / "categories.json"
    import json
    with open(categories_path, 'w') as f:
        json.dump(sample_categories, f)
    return categories_path


@pytest.fixture
def populated_dir(temp_dir):
    """Create a directory with sample files."""
    source_dir = temp_dir / "test_source"
    source_dir.mkdir()

    files = {
        "photo.jpg": "fake jpeg content",
        "document.pdf": "fake pdf content",
        "script.py": "print('hello world')",
        "style.css": "body { color: red; }",
        "readme.txt": "This is a readme",
        "image.png": "fake png content",
    }

    for name, content in files.items():
        (source_dir / name).write_text(content)

    return source_dir