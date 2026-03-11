# Quick Start Guide - Dependency Setup

## 1-Minute Setup

```bash
# Clone repository
git clone <repository-url>
cd red-shadow-ambani

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python setup_dependencies.py --verify
```

## Installation Options

### Option 1: Full Installation (Recommended)
```bash
make install
# or
pip install -r requirements.txt
```

**Includes:**
- Machine Learning (scikit-learn, TensorFlow)
- Network Analysis (scapy, GeoIP2)
- Memory Forensics (psutil, YARA)
- AI Decision Engine (transformers, nashpy)
- All features enabled

**Size:** ~1.5 GB

### Option 2: Minimal Installation
```bash
make install-minimal
# or
python setup_dependencies.py --mode minimal
```

**Includes:**
- Core functionality only
- Configuration and logging
- Database support
- No ML, no network analysis

**Size:** ~50 MB

### Option 3: Development Installation
```bash
make install-dev
# or
pip install -r requirements-dev.txt
```

**Includes:**
- Everything from full installation
- Testing tools (pytest, hypothesis)
- Linting tools (black, flake8, mypy)
- Profiling tools
- Documentation tools

**Size:** ~2 GB

## Verify Installation

```bash
# Quick verification
python setup_dependencies.py --verify

# Or using make
make verify
```

## Common Issues & Solutions

### Issue: TensorFlow installation fails

**Solution 1 - CPU only:**
```bash
pip install tensorflow-cpu>=2.8.0,<3.0.0
```

**Solution 2 - Use PyTorch instead:**
```bash
# Edit requirements.txt: comment TensorFlow, uncomment PyTorch
pip install torch>=1.10.0,<2.0.0
```

### Issue: Scapy requires root permissions

**Linux/Mac:**
```bash
sudo setcap cap_net_raw+ep $(which python)
```

**Windows:**
- Run terminal as Administrator

### Issue: YARA compilation fails

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential python3-dev
pip install yara-python
```

**Windows:**
- Install Visual C++ Build Tools
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Issue: Out of memory during installation

**Solution:**
```bash
# Install packages one at a time
pip install scikit-learn
pip install tensorflow
pip install transformers
# etc.
```

## External Dependencies

### 1. GeoIP2 Database (Optional but recommended)

```bash
# 1. Sign up at MaxMind
# https://www.maxmind.com/en/geolite2/signup

# 2. Download databases
# - GeoLite2-City.mmdb
# - GeoLite2-Country.mmdb

# 3. Place in directory
mkdir -p ambani_integration/data/geoip/
# Copy .mmdb files to this directory
```

### 2. YARA Rules (Optional but recommended)

```bash
# Clone community rules
git clone https://github.com/Yara-Rules/rules.git
mkdir -p ambani_integration/data/yara_rules/
cp -r rules/* ambani_integration/data/yara_rules/
```

### 3. Lua Decompiler (Optional)

```bash
# Download unluac.jar
wget https://sourceforge.net/projects/unluac/files/latest/download -O unluac.jar
mkdir -p ambani_integration/tools/
mv unluac.jar ambani_integration/tools/

# Verify Java is installed
java -version
```

## Testing Your Installation

```bash
# Run basic tests
pytest tests/ -v

# Run with coverage
make test

# Run specific test
pytest tests/test_config.py -v
```

## Next Steps

1. **Configure the system:**
   ```bash
   cp config.example.json config.json
   # Edit config.json with your settings
   ```

2. **Run your first analysis:**
   ```bash
   python -m ambani_integration --help
   ```

3. **Read the documentation:**
   - See `DEPENDENCIES.md` for detailed dependency info
   - See `README.md` for usage instructions
   - See `docs/` for full documentation

## Updating Dependencies

```bash
# Check for updates
pip list --outdated

# Update all
make update

# Update specific package
pip install --upgrade package-name
```

## Uninstalling

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Or keep venv and just uninstall packages
pip uninstall -r requirements.txt -y
```

## Getting Help

- **Dependency issues:** See `DEPENDENCIES.md`
- **Installation issues:** Check this guide
- **Usage issues:** See `README.md`
- **Bug reports:** Open an issue on GitHub

## Useful Commands

```bash
# Show installed packages
pip list

# Show dependency tree
pipdeptree

# Check for vulnerabilities
safety check

# Generate requirements snapshot
pip freeze > requirements-snapshot.txt

# Clean cache files
make clean
```

## Platform-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- Some packages require Visual C++ Build Tools
- Run as Administrator for network capture

### Linux
- Use `sudo` for system-wide installation
- Install build tools: `sudo apt-get install build-essential python3-dev`
- Set capabilities for packet capture

### macOS
- Use Homebrew for system dependencies
- May need Xcode Command Line Tools: `xcode-select --install`
- Use `sudo` for packet capture

## Docker Alternative

If you prefer Docker:

```bash
# Build image
docker build -t red-shadow-ambani .

# Run container
docker run -it --network=host red-shadow-ambani

# Run with volume mount
docker run -it -v $(pwd)/data:/app/data red-shadow-ambani
```

## Performance Tips

1. **Use SSD:** Install on SSD for faster package installation
2. **Parallel installation:** Use `pip install --use-feature=fast-deps`
3. **Cache wheels:** Keep pip cache for faster reinstalls
4. **Virtual environment:** Always use venv to avoid conflicts

## Troubleshooting Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] pip upgraded to latest version
- [ ] Sufficient disk space (~2 GB)
- [ ] Internet connection stable
- [ ] No firewall blocking pip
- [ ] Build tools installed (if needed)
- [ ] Administrator/sudo access (if needed)

## Support

For issues not covered here:
1. Check `DEPENDENCIES.md` for detailed info
2. Search existing GitHub issues
3. Create a new issue with:
   - Python version (`python --version`)
   - OS and version
   - Error message
   - Steps to reproduce
