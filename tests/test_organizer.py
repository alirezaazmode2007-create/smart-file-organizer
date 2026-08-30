"""
Tests for Smart File Organizer.
"""

import os
import json
import shutil
import tempfile
import pytest
from pathlib import Path

from smart_file_organizer.main import (
    get_file_categories,
    sort_file_categories,
    OrganizeReport,
    FileOperation,
    get_categories_path,
)


class TestOrganizeReport:
    """Tests for OrganizeReport class."""

    def test_report_initialization(self):
        report = OrganizeReport(source_directory="/test/path")
        assert report.source_directory == "/test/path"
        assert report.operations == []
        assert report.start_time is not None
        assert report.end_time is None

    def test_add_operation(self):
        report = OrganizeReport()
        op = FileOperation(
            original_name="test.txt",
            action="moved",
            destination_folder="Documents"
        )
        report.add_operation(op)
        assert len(report.operations) == 1
        assert report.operations[0].original_name == "test.txt"

    def test_get_summary(self):
        report = OrganizeReport()
        report.add_operation(FileOperation("a.txt", "moved", "Documents"))
        report.add_operation(FileOperation("b.txt", "moved", "Documents"))
        report.add_operation(FileOperation("c.jpg", "renamed", "Images", "c(1).jpg"))
        report.add_operation(FileOperation("d.pdf", "deleted", "Documents"))

        summary = report.get_summary()
        assert summary["moved"] == 2
        assert summary["renamed"] == 1
        assert summary["deleted"] == 1


class TestFileCategories:
    """Tests for file categorization."""

    def test_get_categories_path(self):
        path = get_categories_path()
        assert os.path.exists(path)
        assert path.endswith("categories.json")

    def test_get_file_categories_basic(self, tmp_path):
        # Create a temporary categories file
        categories = {
            "images": {
                "extensions": [".jpg", ".png"],
                "folder_name": "Images",
                "icon": "🖼️"
            },
            "documents": {
                "extensions": [".txt", ".pdf"],
                "folder_name": "Documents",
                "icon": "📄"
            }
        }
        categories_file = tmp_path / "categories.json"
        with open(categories_file, 'w') as f:
            json.dump(categories, f)

        # Test with the temporary file
        original_get_categories_path = get_categories_path
        import smart_file_organizer.main as main_module
        main_module.get_categories_path = lambda: str(categories_file)

        try:
            report = OrganizeReport()
            files = ["photo.jpg", "doc.txt", "unknown.xyz"]
            result = get_file_categories(files, report)

            assert "photo.jpg" in result
            assert result["photo.jpg"]["folder_name"] == "Images"
            assert "doc.txt" in result
            assert result["doc.txt"]["folder_name"] == "Documents"
            assert "unknown.xyz" not in result
        finally:
            main_module.get_categories_path = original_get_categories_path

    def test_get_file_categories_case_insensitive(self, tmp_path):
        categories = {
            "images": {
                "extensions": [".JPG", ".PNG"],
                "folder_name": "Images",
                "icon": "🖼️"
            }
        }
        categories_file = tmp_path / "categories.json"
        with open(categories_file, 'w') as f:
            json.dump(categories, f)

        import smart_file_organizer.main as main_module
        original_get_categories_path = main_module.get_categories_path
        main_module.get_categories_path = lambda: str(categories_file)

        try:
            report = OrganizeReport()
            files = ["photo.jpg", "PIC.JPG", "image.Png"]
            result = get_file_categories(files, report)

            assert "photo.jpg" in result
            assert "PIC.JPG" in result
            assert "image.Png" in result
        finally:
            main_module.get_categories_path = original_get_categories_path


class TestSortFileCategories:
    """Tests for file sorting functionality."""

    def test_sort_file_categories_basic_move(self, tmp_path):
        # Create test files
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        (source_dir / "test.txt").write_text("test content")
        (source_dir / "image.jpg").write_text("fake image")

        # Setup categories
        categories = {
            "test.txt": {"folder_name": "Documents", "icon": "📄"},
            "image.jpg": {"folder_name": "Images", "icon": "🖼️"}
        }

        report = OrganizeReport(source_directory=str(source_dir))
        sort_file_categories(str(source_dir), categories, report)

        # Check files were moved
        assert (source_dir / "Documents" / "test.txt").exists()
        assert (source_dir / "Images" / "image.jpg").exists()
        assert not (source_dir / "test.txt").exists()
        assert not (source_dir / "image.jpg").exists()

        # Check report
        summary = report.get_summary()
        assert summary["moved"] == 2

    def test_sort_file_categories_skip_nonexistent(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        categories = {
            "nonexistent.txt": {"folder_name": "Documents", "icon": "📄"}
        }

        report = OrganizeReport(source_directory=str(source_dir))
        sort_file_categories(str(source_dir), categories, report)

        summary = report.get_summary()
        assert summary["error"] == 1
        assert "Source file not found" in report.operations[0].error_message


class TestIntegration:
    """Integration tests."""

    def test_full_organize_flow(self, tmp_path):
        """Test the complete organization flow."""
        source_dir = tmp_path / "test_files"
        source_dir.mkdir()

        # Create various test files
        test_files = {
            "photo.jpg": "fake jpg",
            "document.pdf": "fake pdf",
            "script.py": "print('hello')",
            "archive.zip": "fake zip",
            "song.mp3": "fake mp3",
            "video.mp4": "fake mp4",
            "unknown.xyz": "unknown",
        }

        for name, content in test_files.items():
            (source_dir / name).write_text(content)

        # Copy categories file to temp location
        import smart_file_organizer.main as main_module
        original_get_categories_path = main_module.get_categories_path
        categories_path = Path(__file__).parent.parent / "config" / "categories.json"
        main_module.get_categories_path = lambda: str(categories_path)

        try:
            # Get file categories
            all_files = [f for f in os.listdir(source_dir) if not f.startswith('.') and '.' in f]
            report = OrganizeReport(source_directory=str(source_dir))
            file_categories = get_file_categories(all_files, report)

            # Sort files
            sort_file_categories(str(source_dir), file_categories, report)

            # Verify organization
            assert (source_dir / "Images" / "photo.jpg").exists()
            assert (source_dir / "Documents" / "document.pdf").exists()
            assert (source_dir / "Code" / "script.py").exists()
            assert (source_dir / "Archives" / "archive.zip").exists()
            assert (source_dir / "Music" / "song.mp3").exists()
            assert (source_dir / "Videos" / "video.mp4").exists()

            # Unknown file should remain in root (not categorized)
            # Actually it gets skipped
            summary = report.get_summary()
            assert summary["moved"] == 6
            assert summary.get("skipped", 0) >= 1  # unknown.xyz
        finally:
            main_module.get_categories_path = original_get_categories_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])