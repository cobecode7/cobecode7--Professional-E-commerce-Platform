#!/usr/bin/env python3
"""
Validation script for professional e-commerce project setup.
This script checks if all required components are properly configured.
"""

import os
import subprocess
import sys
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def check_tool_availability():
    """Check if required development tools are available."""
    tools = {
        'uv': 'Python package manager',
        'node': 'Node.js runtime',
        'npm': 'Node.js package manager',
        'docker': 'Container platform',
        'git': 'Version control'
    }
    
    print(f"{Colors.BLUE}🔧 Checking development tools...{Colors.END}")
    
    for tool, description in tools.items():
        try:
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip().split('\n')[0]
            print(f"  {Colors.GREEN}✅ {tool}: {version}{Colors.END}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  {Colors.RED}❌ {tool} ({description}) not found{Colors.END}")
            return False
    
    return True


def validate_project_structure():
    """Validate the project directory structure."""
    print(f"\n{Colors.BLUE}📁 Validating project structure...{Colors.END}")
    
    required_dirs = [
        "backend/apps/accounts",
        "backend/apps/products", 
        "backend/apps/orders",
        "backend/apps/reviews",
        "backend/apps/core",
        "backend/config/settings",
        "frontend/src/app",
        "frontend/src/components",
        "frontend/src/lib",
        "docs",
        "scripts",
        ".github/workflows"
    ]
    
    required_files = [
        "agent.md",
        "init_project.sh",
        "README.md",
        ".gitignore",
        ".pre-commit-config.yaml",
        "docker-compose.yml"
    ]
    
    missing_dirs = []
    missing_files = []
    
    # Check directories
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
        else:
            print(f"  {Colors.GREEN}✅ {dir_path}/{Colors.END}")
    
    # Check files
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  {Colors.GREEN}✅ {file_path}{Colors.END}")
    
    if missing_dirs:
        print(f"\n  {Colors.RED}❌ Missing directories:{Colors.END}")
        for dir_path in missing_dirs:
            print(f"    - {dir_path}")
    
    if missing_files:
        print(f"\n  {Colors.RED}❌ Missing files:{Colors.END}")
        for file_path in missing_files:
            print(f"    - {file_path}")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0


def check_configuration_files():
    """Check if configuration files have proper content."""
    print(f"\n{Colors.BLUE}⚙️  Checking configuration files...{Colors.END}")
    
    config_checks = {
        "agent.md": ["uv + ruff", "هيكل المشروع الاحترافي", "معايير التطوير المهنية"],
        ".gitignore": ["node_modules/", "__pycache__/", ".env"],
        "docker-compose.yml": ["postgres:", "redis:", "backend:", "frontend:"]
    }
    
    all_good = True
    
    for file_path, required_content in config_checks.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            missing_content = []
            for req in required_content:
                if req not in content:
                    missing_content.append(req)
            
            if missing_content:
                print(f"  {Colors.YELLOW}⚠️  {file_path} missing content:{Colors.END}")
                for missing in missing_content:
                    print(f"    - {missing}")
                all_good = False
            else:
                print(f"  {Colors.GREEN}✅ {file_path} properly configured{Colors.END}")
        else:
            print(f"  {Colors.RED}❌ {file_path} not found{Colors.END}")
            all_good = False
    
    return all_good


def check_professional_standards():
    """Check if professional development standards are met."""
    print(f"\n{Colors.BLUE}🏆 Checking professional standards...{Colors.END}")
    
    standards = {
        "Pre-commit hooks": ".pre-commit-config.yaml",
        "CI/CD pipeline": ".github/workflows/ci.yml", 
        "Documentation": "docs/CONTRIBUTING.md",
        "Docker setup": "docker-compose.yml",
        "Professional structure": "backend/apps/core/permissions.py"
    }
    
    all_standards_met = True
    
    for standard, file_path in standards.items():
        if os.path.exists(file_path):
            print(f"  {Colors.GREEN}✅ {standard}{Colors.END}")
        else:
            print(f"  {Colors.RED}❌ {standard} - missing {file_path}{Colors.END}")
            all_standards_met = False
    
    return all_standards_met


def generate_report():
    """Generate a comprehensive validation report."""
    print(f"\n{Colors.BOLD}📊 VALIDATION REPORT{Colors.END}")
    print("=" * 50)
    
    checks = [
        ("Development Tools", check_tool_availability),
        ("Project Structure", validate_project_structure),
        ("Configuration Files", check_configuration_files),
        ("Professional Standards", check_professional_standards)
    ]
    
    results = {}
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"{Colors.RED}❌ Error in {check_name}: {e}{Colors.END}")
            results[check_name] = False
            all_passed = False
    
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    for check_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS" if result else f"{Colors.RED}❌ FAIL"
        print(f"  {check_name}: {status}{Colors.END}")
    
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All checks passed! Project is ready for professional development.{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Some checks failed. Please fix the issues above.{Colors.END}")
        return 1


def main():
    """Main validation function."""
    print(f"{Colors.BOLD}🔍 Professional E-commerce Project Validator{Colors.END}")
    print(f"{Colors.BLUE}Validating project setup and configuration...{Colors.END}\n")
    
    # Run validation from current directory
    return generate_report()


if __name__ == "__main__":
    sys.exit(main())