"""
Smart File Organizer - Automatically organize files by category.

A powerful, cross-platform Python tool to automatically organize files in a
directory by category (images, videos, documents, audio, archives, code, etc.).
Features duplicate handling, customizable categories, and a clean CLI interface.
"""

__version__ = "1.0.0"
__author__ = "Alireza"
__email__ = "alireza@example.com"
__license__ = "MIT"

from .main import main, OrganizeReport, FileOperation

__all__ = ["main", "OrganizeReport", "FileOperation"]