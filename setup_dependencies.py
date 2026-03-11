#!/usr/bin/env python3
"""
Dependency Setup Script for RED-SHADOW v4.0 - Ambani Integration

This script helps install and verify dependencies with various options.

Usage:
    python setup_dependencies.py --mode full      # Full installation
    python setup_dependencies.py --mode minimal   # Minimal installation
    python setup_dependencies.py --mode dev       # Development installation
    python setup_dependencies.py --verify         # Verify installation
"""

import argparse
import subprocess
import sys
import os
from typing import List, Tuple, Optional


class DependencyInstaller:
    """Manages dependency installation for RED-SHADOW Ambani Integration"""
    
    def __init__(self):
        self.python_cmd = sys.executable
        self.pip_cmd = [self.python_cmd, "-m", "pip"]
        
    def check_python_version(self) -> bool:
        """Check if Python version is 3.8+"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version"""
        print("\n📦 Upgrading pip...")
        try:
            subprocess.check_call(
                self.pip_cmd + ["install", "--upgrade", "pip"],
                stdout=subprocess.DEVNULL
            )
            print("✓ pip upgraded")
            return True
        except subprocess.CalledProcessError:
            print("⚠ Failed to upgrade pip (continuing anyway)")
            return False
    
    def install_requirements(self, requirements_file: str) -> bool:
        """Install dependencies from requirements file"""
        if not os.path.exists(requirements_file):
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        print(f"\n📦 Installing dependencies from {requirements_file}...")
        print("   This may take several minutes...")
        
        try:
            subprocess.check_call(
                self.pip_cmd + ["install", "-r", requirements_file]
            )
            print(f"✓ Dependencies installed from {requirements_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def install_minimal(self) -> bool:
        """Install minimal dependencies"""
        print("\n📦 Installing minimal dependencies...")
        minimal_packages = [
            "pyyaml>=6.0",
            "colorama>=0.4.4",
            "rich>=12.0.0",
            "click>=8.0.0",
            "requests>=2.26.0",
            "sqlalchemy>=1.4.0",
            "python-dotenv>=0.19.0"
        ]
        
        try:
            subprocess.check_call(
                self.pip_cmd + ["install"] + minimal_packages
            )
            print("✓ Minimal dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install minimal dependencies: {e}")
            return False
    
    def verify_imports(self) -> List[Tuple[str, bool, Optional[str]]]:
        """Verify that key packages can be imported"""
        print("\n🔍 Verifying installations...")
        
        packages = [
            ("yaml", "PyYAML"),
            ("sklearn", "scikit-learn"),
            ("numpy", "numpy"),
            ("pandas", "pandas"),
            ("tensorflow", "TensorFlow"),
            ("transformers", "transformers"),
            ("scapy", "scapy"),
            ("psutil", "psutil"),
            ("yara", "yara-python"),
            ("lupa", "lupa"),
            ("nashpy", "nashpy"),
            ("gym", "gym"),
            ("matplotlib", "matplotlib"),
            ("sqlalchemy", "SQLAlchemy"),
            ("click", "click"),
            ("rich", "rich"),
        ]
        
        results = []
        for module_name, package_name in packages:
            try:
                __import__(module_name)
                results.append((package_name, True, None))
                print(f"  ✓ {package_name}")
            except ImportError as e:
                results.append((package_name, False, str(e)))
                print(f"  ❌ {package_name}: {e}")
        
        return results
    
    def check_external_tools(self) -> List[Tuple[str, bool, Optional[str]]]:
        """Check for external tools"""
        print("\n🔍 Checking external tools...")
        
        tools = []
        
        # Check for Java (required for unluac)
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                tools.append(("Java (for unluac)", True, None))
                print("  ✓ Java (for unluac)")
            else:
                tools.append(("Java (for unluac)", False, "Not found"))
                print("  ⚠ Java not found (required for .fxap decompilation)")
        except FileNotFoundError:
            tools.append(("Java (for unluac)", False, "Not found"))
            print("  ⚠ Java not found (required for .fxap decompilation)")
        
        # Check for GeoIP database
        geoip_path = "ambani_integration/data/geoip/GeoLite2-City.mmdb"
        if os.path.exists(geoip_path):
            tools.append(("GeoIP2 Database", True, None))
            print("  ✓ GeoIP2 Database")
        else:
            tools.append(("GeoIP2 Database", False, "Not found"))
            print("  ⚠ GeoIP2 Database not found (download from MaxMind)")
        
        # Check for YARA rules
        yara_path = "ambani_integration/data/yara_rules"
        if os.path.exists(yara_path) and os.listdir(yara_path):
            tools.append(("YARA Rules", True, None))
            print("  ✓ YARA Rules")
        else:
            tools.append(("YARA Rules", False, "Not found"))
            print("  ⚠ YARA Rules not found (clone from Yara-Rules repo)")
        
        return tools
    
    def print_summary(self, success: bool):
        """Print installation summary"""
        print("\n" + "="*60)
        if success:
            print("✓ Installation completed successfully!")
            print("\nNext steps:")
            print("1. Download GeoIP2 database from MaxMind")
            print("2. Clone YARA rules repository")
            print("3. Download unluac.jar (if needed)")
            print("4. Run: python setup_dependencies.py --verify")
        else:
            print("⚠ Installation completed with warnings")
            print("\nSome dependencies may have failed to install.")
            print("Check the output above for details.")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Install dependencies for RED-SHADOW Ambani Integration"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "minimal", "dev"],
        default="full",
        help="Installation mode (default: full)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify installation without installing"
    )
    parser.add_argument(
        "--no-upgrade-pip",
        action="store_true",
        help="Skip pip upgrade"
    )
    
    args = parser.parse_args()
    
    installer = DependencyInstaller()
    
    print("="*60)
    print("RED-SHADOW v4.0 - Ambani Integration")
    print("Dependency Installation Script")
    print("="*60)
    
    # Check Python version
    if not installer.check_python_version():
        sys.exit(1)
    
    # Verify mode
    if args.verify:
        installer.verify_imports()
        installer.check_external_tools()
        return
    
    # Upgrade pip
    if not args.no_upgrade_pip:
        installer.upgrade_pip()
    
    # Install based on mode
    success = True
    if args.mode == "minimal":
        success = installer.install_minimal()
    elif args.mode == "dev":
        success = installer.install_requirements("requirements-dev.txt")
    else:  # full
        success = installer.install_requirements("requirements.txt")
    
    # Verify installation
    if success:
        installer.verify_imports()
        installer.check_external_tools()
    
    # Print summary
    installer.print_summary(success)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
