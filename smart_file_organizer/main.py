import os
import json
import shutil
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class FileOperation:
    """Represents a file operation for reporting."""
    original_name: str
    action: str  # moved, renamed, deleted, skipped, error
    destination_folder: str = ""
    new_name: str = ""
    error_message: str = ""


@dataclass
class OrganizeReport:
    """Report of all file operations performed."""
    operations: List[FileOperation] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    source_directory: str = ""

    def add_operation(self, op: FileOperation):
        self.operations.append(op)

    def get_summary(self) -> Dict[str, int]:
        summary = {}
        for op in self.operations:
            summary[op.action] = summary.get(op.action, 0) + 1
        return summary

    def print_report(self):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        print("\n" + "=" * 70)
        print("📊 FILE ORGANIZATION REPORT")
        print("=" * 70)
        print(f"📁 Source Directory: {self.source_directory}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🕐 Completed: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 70)

        summary = self.get_summary()
        print(f"\n📈 SUMMARY:")
        for action, count in summary.items():
            icon = {
                "moved": "✅",
                "renamed": "✏️",
                "deleted": "🗑️",
                "skipped": "⏭️",
                "error": "❌"
            }.get(action, "📋")
            print(f"   {icon} {action.capitalize()}: {count}")

        print(f"\n📋 DETAILED OPERATIONS:")
        print("-" * 70)

        current_folder = None
        for op in self.operations:
            if op.destination_folder and op.destination_folder != current_folder:
                current_folder = op.destination_folder
                print(f"\n📂 {current_folder}/")

            if op.action == "moved":
                print(f"   ✅ {op.original_name}")
            elif op.action == "renamed":
                print(f"   ✏️ {op.original_name} → {op.new_name}")
            elif op.action == "deleted":
                print(f"   🗑️ {op.original_name} (deleted)")
            elif op.action == "skipped":
                print(f"   ⏭️ {op.original_name} (skipped - user exited)")
            elif op.action == "error":
                print(f"   ❌ {op.original_name} - Error: {op.error_message}")

        print("\n" + "=" * 70)
        print(f"Total files processed: {len(self.operations)}")
        print("=" * 70)


def get_categories_path() -> str:
    """Get the path to the categories config file."""
    # Check in config directory first, then fallback to root
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "categories.json")
    config_path = os.path.normpath(config_path)
    if os.path.exists(config_path):
        return config_path
    # Fallback to root directory
    root_path = os.path.join(os.path.dirname(__file__), "..", "FILE_CATEGORIES.json")
    return os.path.normpath(root_path)


def get_directory_path() -> str:
    while True:
        try:
            dir_path = input('Please enter the directory path: ').strip()
            if not dir_path:
                print("Directory path cannot be empty. Please try again.")
                continue
            if not os.path.exists(dir_path):
                print(f"Directory '{dir_path}' does not exist. Please try again.")
                continue
            if not os.path.isdir(dir_path):
                print(f"'{dir_path}' is not a directory. Please try again.")
                continue
            return dir_path
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            exit(1)
        except Exception as e:
            print(f"Error: {e}. Please try again.")


def get_file_categories(list_file: List[str], report: OrganizeReport) -> Dict[str, Dict]:
    file_info = {}
    categories_path = get_categories_path()

    try:
        with open(categories_path, 'r', encoding='utf-8') as f:
            FILE_CATEGORIES = json.load(f)
    except FileNotFoundError:
        print(f"Error: Categories file not found at {categories_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in categories file: {e}")
        return {}
    except Exception as e:
        print(f"Error reading categories file: {e}")
        return {}

    for file in list_file:
        try:
            matched = False
            for category, info in FILE_CATEGORIES.items():
                if file.lower().endswith(tuple(ext.lower() for ext in info['extensions'])):
                    file_info[file] = {"folder_name": info['folder_name'], "icon": info['icon']}
                    matched = True
                    break
            if not matched:
                report.add_operation(FileOperation(
                    original_name=file,
                    action="skipped",
                    error_message="No matching category found"
                ))
        except Exception as e:
            report.add_operation(FileOperation(
                original_name=file,
                action="error",
                error_message=str(e)
            ))

    return file_info


def sort_file_categories(dir_path: str, file_categories: Dict[str, Dict], report: OrganizeReport):
    for filename, info in file_categories.items():
        try:
            folder_name = info['folder_name']
            destination_dir = os.path.join(dir_path, folder_name)
            os.makedirs(destination_dir, exist_ok=True)

            source = os.path.join(dir_path, filename)
            destination_check = os.path.join(destination_dir, filename)

            if not os.path.exists(source):
                report.add_operation(FileOperation(
                    original_name=filename,
                    action="error",
                    destination_folder=folder_name,
                    error_message="Source file not found"
                ))
                continue

            if not os.path.exists(destination_check):
                shutil.move(source, destination_dir)
                report.add_operation(FileOperation(
                    original_name=filename,
                    action="moved",
                    destination_folder=folder_name
                ))
            else:
                while True:
                    rename_or_delete = input(
                        f"File '{filename}' already exists in {folder_name}. "
                        "Delete or Rename or Exit: "
                    ).strip().lower()

                    if rename_or_delete == 'rename':
                        try:
                            ask = int(input('Auto rename=1 || Rename with custom name=2: '))
                        except ValueError:
                            print('Invalid input. Please enter 1 or 2.')
                            continue

                        if ask == 1:
                            i = 1
                            file_name, ext = os.path.splitext(filename)
                            while True:
                                new_file_name = f'{file_name}({i}){ext}'
                                new_dest = os.path.join(destination_dir, new_file_name)
                                if not os.path.exists(new_dest):
                                    try:
                                        os.rename(source, os.path.join(dir_path, new_file_name))
                                        source = os.path.join(dir_path, new_file_name)
                                        shutil.move(source, destination_dir)
                                        report.add_operation(FileOperation(
                                            original_name=filename,
                                            action="renamed",
                                            destination_folder=folder_name,
                                            new_name=new_file_name
                                        ))
                                    except Exception as e:
                                        report.add_operation(FileOperation(
                                            original_name=filename,
                                            action="error",
                                            destination_folder=folder_name,
                                            error_message=f"Rename failed: {e}"
                                        ))
                                    break
                                i += 1
                            break

                        elif ask == 2:
                            while True:
                                print(f'Filename: {filename}')
                                ext = os.path.splitext(filename)[1]
                                new_name = input('New file name without extension: ').strip()
                                if not new_name:
                                    print("Name cannot be empty.")
                                    continue
                                check_file_name = new_name + ext
                                check_dest = os.path.join(destination_dir, check_file_name)
                                if not os.path.exists(check_dest):
                                    try:
                                        filename = new_name + ext
                                        os.rename(source, os.path.join(dir_path, filename))
                                        shutil.move(os.path.join(dir_path, filename), destination_dir)
                                        report.add_operation(FileOperation(
                                            original_name=filename,
                                            action="renamed",
                                            destination_folder=folder_name,
                                            new_name=check_file_name
                                        ))
                                    except Exception as e:
                                        report.add_operation(FileOperation(
                                            original_name=filename,
                                            action="error",
                                            destination_folder=folder_name,
                                            error_message=f"Rename failed: {e}"
                                        ))
                                    break
                                print('The new file name exists. Please change the file name.')
                            break
                        else:
                            print('Invalid input. Please enter 1 or 2.')

                    elif rename_or_delete == 'delete':
                        try:
                            ask = int(input('Delete which one? This file=1 or the file in the folder=2: '))
                        except ValueError:
                            print('Invalid input. Please enter 1 or 2.')
                            continue

                        if ask == 1:
                            try:
                                os.remove(source)
                                report.add_operation(FileOperation(
                                    original_name=filename,
                                    action="deleted",
                                    destination_folder=folder_name
                                ))
                            except Exception as e:
                                report.add_operation(FileOperation(
                                    original_name=filename,
                                    action="error",
                                    destination_folder=folder_name,
                                    error_message=f"Delete failed: {e}"
                                ))
                            break

                        elif ask == 2:
                            try:
                                os.remove(destination_check)
                                shutil.move(source, destination_dir)
                                report.add_operation(FileOperation(
                                    original_name=filename,
                                    action="moved",
                                    destination_folder=folder_name,
                                    new_name=filename + " (replaced existing)"
                                ))
                            except Exception as e:
                                report.add_operation(FileOperation(
                                    original_name=filename,
                                    action="error",
                                    destination_folder=folder_name,
                                    error_message=f"Replace failed: {e}"
                                ))
                            break
                        else:
                            print('Invalid input. Please enter 1 or 2.')

                    elif rename_or_delete == 'exit':
                        report.add_operation(FileOperation(
                            original_name=filename,
                            action="skipped",
                            destination_folder=folder_name
                        ))
                        break
                    else:
                        print('Invalid input. Please enter Delete, Rename, or Exit.')

        except PermissionError:
            report.add_operation(FileOperation(
                original_name=filename,
                action="error",
                error_message="Permission denied"
            ))
        except Exception as e:
            report.add_operation(FileOperation(
                original_name=filename,
                action="error",
                error_message=str(e)
            ))


def main():
    print("🗂️  Smart File Organizer")
    print("=" * 40)

    report = OrganizeReport()

    dir_path = get_directory_path()
    report.source_directory = dir_path

    try:
        all_files_in_dir = os.listdir(dir_path)
    except PermissionError:
        print(f"Error: Permission denied accessing '{dir_path}'")
        exit(1)
    except Exception as e:
        print(f"Error listing directory: {e}")
        exit(1)

    files_in_dir_with = [
        x for x in all_files_in_dir
        if not x.startswith('.') and '.' in x and os.path.isfile(os.path.join(dir_path, x))
    ]

    if not files_in_dir_with:
        print("No files to organize in the directory.")
        return

    print(f"\n📄 Found {len(files_in_dir_with)} files to process...")

    file_categories = get_file_categories(files_in_dir_with, report)

    if file_categories:
        sort_file_categories(dir_path, file_categories, report)
    else:
        print("No files matched any category.")

    report.print_report()


if __name__ == "__main__":
    main()