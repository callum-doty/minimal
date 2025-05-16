#!/usr/bin/env python
"""
Project structure checker script to diagnose import issues.
"""

import os
import sys
import importlib
import pkgutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_directory_structure(path="."):
    """Check the directory structure of the project."""
    logger.info(f"Checking directory structure in {os.path.abspath(path)}")

    for root, dirs, files in os.walk(path):
        # Skip virtual environment and hidden directories
        if any(
            excluded in root
            for excluded in ["/venv/", "/.git/", "/__pycache__/", ".pyc"]
        ):
            continue

        level = root.replace(path, "").count(os.sep)
        indent = " " * 4 * level
        logger.info(f"{indent}└── {os.path.basename(root)}/")

        sub_indent = " " * 4 * (level + 1)
        for file in sorted(files):
            if file.endswith(".py"):
                logger.info(f"{sub_indent}└── {file}")


def check_python_path():
    """Check the Python path."""
    logger.info("Python Path:")
    for i, path in enumerate(sys.path):
        logger.info(f"  {i+1}. {path}")


def check_package_structure(package_name="src"):
    """Check if a package can be imported and explore its structure."""
    logger.info(f"Checking package structure for '{package_name}'...")

    try:
        # Try to import the package
        package = importlib.import_module(package_name)
        logger.info(f"Successfully imported {package_name} from {package.__file__}")

        # Check if it's actually a package
        if not hasattr(package, "__path__"):
            logger.info(f"{package_name} is a module, not a package")
            return

        # List all submodules
        logger.info(f"Submodules of {package_name}:")

        for _, name, is_pkg in pkgutil.iter_modules(
            package.__path__, package.__name__ + "."
        ):
            try:
                module = importlib.import_module(name)
                status = "package" if is_pkg else "module"
                logger.info(f"  ✓ {name} ({status}) - {module.__file__}")

                # If it's a package, check for __init__.py
                if is_pkg:
                    init_path = os.path.join(
                        os.path.dirname(module.__file__), "__init__.py"
                    )
                    if os.path.exists(init_path):
                        logger.info(f"    ✓ Has __init__.py")
                    else:
                        logger.warning(f"    ✗ Missing __init__.py!")
            except ImportError as e:
                logger.error(f"  ✗ Failed to import {name}: {str(e)}")
    except ImportError as e:
        logger.error(f"Failed to import {package_name}: {str(e)}")


def check_specific_module(module_path="src.catalog.routes"):
    """Check if a specific module exists and can be imported."""
    logger.info(f"Checking for specific module: {module_path}")

    # First check if the directory exists
    if module_path.startswith("src."):
        parts = module_path.split(".")
        dir_path = os.path.join(*parts)

        if os.path.exists(dir_path):
            logger.info(f"Directory exists: {dir_path}")

            # Check for __init__.py in the directory
            init_path = os.path.join(dir_path, "__init__.py")
            if os.path.exists(init_path):
                logger.info(f"Found __init__.py in {dir_path}")
            else:
                logger.warning(f"Missing __init__.py in {dir_path}")

            # List python files in directory
            py_files = [f for f in os.listdir(dir_path) if f.endswith(".py")]
            logger.info(f"Python files in {dir_path}: {py_files}")
        else:
            logger.warning(f"Directory does not exist: {dir_path}")

    # Try to import the module
    try:
        module = importlib.import_module(module_path)
        logger.info(f"Successfully imported {module_path} from {module.__file__}")
    except ImportError as e:
        logger.error(f"Failed to import {module_path}: {str(e)}")

        # Try to import parent modules to locate where the import chain breaks
        parts = module_path.split(".")
        for i in range(1, len(parts)):
            parent_module = ".".join(parts[:i])
            try:
                module = importlib.import_module(parent_module)
                logger.info(
                    f"Parent module {parent_module} imported successfully from {module.__file__}"
                )
            except ImportError as e:
                logger.error(
                    f"Failed to import parent module {parent_module}: {str(e)}"
                )
                break


def list_installed_packages():
    """List installed Python packages."""
    logger.info("Installed Python packages:")

    try:
        import pkg_resources

        installed_packages = sorted(
            [f"{pkg.key} {pkg.version}" for pkg in pkg_resources.working_set]
        )
        for package in installed_packages:
            logger.info(f"  {package}")
    except ImportError:
        logger.error("Could not import pkg_resources to list installed packages")


def print_file_content(filepath, max_lines=20):
    """Print the content of a specific file."""
    if os.path.exists(filepath):
        logger.info(f"Content of {filepath} (first {max_lines} lines):")
        try:
            with open(filepath, "r") as f:
                for i, line in enumerate(f):
                    if i < max_lines:
                        logger.info(f"  {i+1}: {line.rstrip()}")
                    else:
                        logger.info(f"  ... (file has more than {max_lines} lines)")
                        break
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
    else:
        logger.warning(f"File not found: {filepath}")


def main():
    """Main function to run all checks."""
    logger.info("=" * 50)
    logger.info("Project Structure Check")
    logger.info("=" * 50)

    # Check Python path
    check_python_path()

    # Check if we're in the right directory
    if not os.path.exists("src"):
        logger.warning("src directory not found in current directory")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Contents: {os.listdir('.')}")

    # Check directory structure
    check_directory_structure("src")

    # Check package structure
    check_package_structure("src")
    check_package_structure("src.catalog")

    # Check specific modules
    check_specific_module("src.catalog.routes")
    check_specific_module("src.catalog.web")

    # Print content of key files
    print_file_content("src/catalog/__init__.py")

    # List installed packages
    list_installed_packages()

    logger.info("=" * 50)
    logger.info("Project Structure Check Complete")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
