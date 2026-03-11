# Dependency Management Guide

## Overview

This document explains the dependencies required for RED-SHADOW v4.0 with Ambani Integration and provides installation instructions.

## Quick Start

### Basic Installation

```bash
# Install all required dependencies
pip install -r requirements.txt

# Or use pip with upgrade flag
pip install --upgrade -r requirements.txt
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Dependency Categories

### 1. Machine Learning & AI (Behavioral Analyzer)

**Purpose:** Anomaly detection, behavior analysis, pattern recognition

- **scikit-learn** (1.0.0+): Isolation Forest, One-Class SVM algorithms
- **numpy** (1.21.0+): Numerical computing foundation
- **pandas** (1.3.0+): Data manipulation and analysis
- **scipy** (1.7.0+): Scientific computing utilities
- **tensorflow** (2.8.0+): Deep learning for Autoencoders
- **keras** (2.8.0+): High-level neural network API

**Alternative:** PyTorch can be used instead of TensorFlow (uncomment in requirements.txt)

### 2. NLP & AI Decision Engine

**Purpose:** AI-based variable renaming, intelligent decision making

- **transformers** (4.20.0+): BERT, GPT models for code analysis
- **tokenizers** (0.12.0+): Fast tokenization for NLP models
- **sentencepiece** (0.1.96+): Tokenization for transformer models

**Use Cases:**
- Renaming obfuscated variables (L0_1, A0_2) to meaningful names
- Understanding code context for better analysis
- Generating human-readable reports

### 3. Network Analysis (Network Monitor, Deep Packet Inspector)

**Purpose:** Real-time traffic monitoring, attack detection

- **scapy** (2.4.5+): Packet capture and manipulation (primary choice)
- **geoip2** (4.5.0+): IP geolocation for attacker profiling
- **maxminddb** (2.2.0+): MaxMind database reader

**Alternative:** pyshark (Wireshark wrapper) can be used instead of scapy

**Note:** Requires GeoIP2 database files (download separately from MaxMind)

### 4. Memory Forensics

**Purpose:** Memory analysis, malware detection, injection detection

- **psutil** (5.8.0+): Process and system monitoring
- **yara-python** (4.2.0+): Malware pattern matching

**Platform-Specific:**
- **pymem** (Windows only): Direct memory manipulation (optional)

### 5. Lua Decompilation & Bytecode Analysis

**Purpose:** Decompiling obfuscated Lua code, .fxap files

- **lupa** (1.13+): Python-Lua bridge for sandbox execution

**External Tools:**
- **unluac**: Java-based Lua decompiler (install separately)
  - Download: https://sourceforge.net/projects/unluac/
  - Requires Java Runtime Environment (JRE)

### 6. Game Theory & Optimization (AI Decision Engine)

**Purpose:** Strategic decision making, exploit prioritization

- **nashpy** (0.0.21+): Nash Equilibrium calculation
- **cvxpy** (1.2.0+): Convex optimization for strategy selection

**Algorithms:**
- A* search for exploit sequencing
- Monte Carlo Tree Search (MCTS)
- Multi-Armed Bandit (Thompson Sampling)
- Game theory modeling

### 7. Reinforcement Learning

**Purpose:** Adaptive testing, learning from feedback

- **gym** (0.21.0+): RL environment framework
- **stable-baselines3** (1.5.0+): Pre-implemented RL algorithms

### 8. Visualization (Security Reporter)

**Purpose:** Generating charts and graphs for reports

- **matplotlib** (3.5.0+): Static plotting
- **seaborn** (0.11.0+): Statistical visualizations
- **plotly** (5.5.0+): Interactive HTML charts

### 9. Database & ORM

**Purpose:** Analysis history, learning feedback storage

- **sqlite3**: Built-in to Python (no installation needed)
- **sqlalchemy** (1.4.0+): ORM for database operations
- **alembic** (1.7.0+): Database schema migrations

### 10. CLI & Logging

**Purpose:** User interface, progress tracking, colored output

- **colorama** (0.4.4+): Cross-platform colored terminal
- **rich** (12.0.0+): Beautiful terminal formatting
- **click** (8.0.0+): CLI argument parsing
- **tqdm** (4.62.0+): Progress bars

## Optional Dependencies

### Platform-Specific

#### Windows
```bash
pip install pywin32>=303
pip install wmi>=1.5.1
```

#### Linux
```bash
pip install python-iptables>=1.0.0
```

### Development Tools
```bash
pip install ipython>=8.0.0
pip install jupyter>=1.0.0
pip install notebook>=6.4.0
```

## External Dependencies

### 1. GeoIP2 Database

**Required for:** IP geolocation in Network Monitor

```bash
# Download GeoLite2 databases (free)
# 1. Sign up at https://www.maxmind.com/en/geolite2/signup
# 2. Download GeoLite2-City.mmdb and GeoLite2-Country.mmdb
# 3. Place in: ambani_integration/data/geoip/
```

### 2. YARA Rules

**Required for:** Malware detection in Memory Forensics

```bash
# Download community YARA rules
git clone https://github.com/Yara-Rules/rules.git
# Place in: ambani_integration/data/yara_rules/
```

### 3. Lua Decompiler (unluac)

**Required for:** .fxap decompilation

```bash
# Download unluac.jar
wget https://sourceforge.net/projects/unluac/files/latest/download -O unluac.jar
# Place in: ambani_integration/tools/unluac.jar
# Requires: Java Runtime Environment (JRE) 8+
```

## Version Constraints Explained

### Upper Bounds (<)
- Prevents breaking changes from major version updates
- Example: `scikit-learn>=1.0.0,<2.0.0` allows 1.x but not 2.x

### Lower Bounds (>=)
- Ensures minimum required features are available
- Example: `tensorflow>=2.8.0` requires at least version 2.8.0

### Why Version Pinning?
- **Stability**: Prevents unexpected breakage from updates
- **Reproducibility**: Ensures consistent behavior across installations
- **Security**: Allows controlled updates after testing

## Troubleshooting

### TensorFlow Installation Issues

**GPU Support:**
```bash
# For NVIDIA GPU support
pip install tensorflow-gpu>=2.8.0,<3.0.0
```

**CPU Only (smaller install):**
```bash
pip install tensorflow-cpu>=2.8.0,<3.0.0
```

### Scapy Permissions (Linux/Mac)

```bash
# Packet capture requires root/sudo
sudo python -m pip install scapy
# Or use capabilities (Linux)
sudo setcap cap_net_raw+ep $(which python)
```

### YARA Compilation Issues

```bash
# Install build dependencies first
# Ubuntu/Debian:
sudo apt-get install build-essential python3-dev
# CentOS/RHEL:
sudo yum install gcc python3-devel
# Then install yara-python
pip install yara-python
```

### Windows-Specific Issues

**Visual C++ Build Tools Required:**
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Required for: yara-python, some ML packages

## Minimal Installation

For testing or limited functionality:

```bash
# Core only (no ML, no network analysis)
pip install pyyaml colorama rich click requests sqlalchemy
```

## Docker Installation

```bash
# Build Docker image with all dependencies
docker build -t red-shadow-ambani .

# Run container
docker run -it --network=host red-shadow-ambani
```

## Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all (use with caution)
pip install --upgrade -r requirements.txt
```

## Dependency Size Estimates

- **Minimal Install**: ~50 MB
- **Full Install (no ML)**: ~200 MB
- **Full Install (with TensorFlow)**: ~1.5 GB
- **Full Install (with PyTorch)**: ~2.0 GB

## Security Considerations

### Verify Package Integrity

```bash
# Use pip with hash checking
pip install --require-hashes -r requirements-hashes.txt
```

### Scan for Vulnerabilities

```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check -r requirements.txt
```

## License Compatibility

All dependencies are compatible with open-source projects:
- **MIT License**: Most packages
- **Apache 2.0**: TensorFlow, transformers
- **BSD License**: scikit-learn, numpy, pandas

## Support

For dependency-related issues:
1. Check this document first
2. Review package documentation
3. Search GitHub issues for the specific package
4. Contact RED-SHADOW support

## Changelog

- **2024-01**: Initial dependency list for Ambani integration
- Added ML/AI dependencies for Behavioral Analyzer
- Added NLP dependencies for AI Decision Engine
- Added network analysis dependencies
- Added game theory and RL dependencies
