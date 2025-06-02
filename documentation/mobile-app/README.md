# 📱 Mobile App Documentation

**iOS Pythonista compatibility and experimental mobile app development**

> **📱 iOS Pythonista**: Wrapper scripts are fully functional on iOS Pythonista - designed to simplify running astropy.py without typing parameters.
> 
> **🧪 EXPERIMENTAL**: A separate native mobile app implementation is in development but not fully tested yet.

---

## 📋 **Table of Contents**

- [🎯 Overview](#-overview)
- [📱 Wrapper Scripts](#-wrapper-scripts)
- [🔧 Setup Instructions](#-setup-instructions)
- [📖 Usage Examples](#-usage-examples)
- [⚠️ Known Limitations](#️-known-limitations)
- [🐛 Troubleshooting](#-troubleshooting)

---

## 🎯 **Overview**

This documentation covers two distinct mobile implementations:

1. **iOS Pythonista Compatibility** (Fully Functional)
2. **Experimental Native Mobile App** (In Development)

### **✅ iOS Pythonista Compatibility (Fully Functional)**
- All 10 wrapper scripts tested and working on desktop AND iOS Pythonista
- Designed specifically to simplify running astropy.py without typing parameters in iOS
- Complete observation planning and scheduling
- Mosaic analysis and trajectory plotting
- Report generation and data export
- Multiple scheduling strategies

### **🧪 Experimental Native Mobile App (In Development)**
- Separate mobile app implementation (not Pythonista-based)
- Not fully tested yet
- Independent of the wrapper scripts
- May have different features and limitations

---

## 📱 **Wrapper Scripts**

All wrapper scripts are located in the `wrappers/` directory and provide simplified access to core functionality:

### **📊 Analysis & Reporting**
- **`run_report_only.py`** - Generate comprehensive observation reports
- **`run_quarters_report.py`** - Quarterly analysis without plots
- **`run_telescope_analysis.py`** - Telescope analysis and listing (8 telescopes)

### **🎯 Scheduling Strategies**
- **`run_longest_duration.py`** - Maximize single object exposure time
- **`run_max_objects.py`** - Observe maximum number of objects
- **`run_optimal_snr.py`** - Optimize signal-to-noise ratio

### **🖼️ Mosaic & Visualization**
- **`run_mosaic_analysis.py`** - Comprehensive mosaic analysis with plots
- **`run_mosaic_plots.py`** - Mosaic trajectory plotting and visualization
- **`run_quarters.py`** - 4-quarter trajectory plots with scheduling
- **`run_with_plots.py`** - Full observation planner with comprehensive plots

---

## 🔧 **Setup Instructions**

### **Desktop Testing (Verified)**
```bash
# All scripts work correctly on desktop systems
cd astropy/wrappers
python run_report_only.py
python run_max_objects.py
python run_mosaic_analysis.py
```

### **iOS Pythonista Setup (Fully Functional)**

#### **1. Install Pythonista**
- Download Pythonista 3 from the App Store
- Ensure you have the latest version

#### **2. Transfer Files**
```python
# Option 1: Use Pythonista's file transfer feature
# Option 2: Use cloud storage (iCloud, Dropbox, etc.)
# Option 3: Use git clone if available
```

#### **3. Install Dependencies**
```python
# In Pythonista console
import pip
pip.main(['install', 'numpy'])
pip.main(['install', 'matplotlib'])
pip.main(['install', 'pytz'])
```

#### **4. Test Basic Functionality**
```python
# Test import
exec(open('wrappers/run_report_only.py').read())
```

---

## 📖 **Usage Examples**

### **Basic Report Generation**
```python
# Direct execution
exec(open('wrappers/run_report_only.py').read())

# Import and run
import sys
sys.path.insert(0, 'wrappers')
import run_report_only
```

### **Scheduling Strategies**
```python
# Maximum objects strategy
exec(open('wrappers/run_max_objects.py').read())

# Optimal SNR strategy
exec(open('wrappers/run_optimal_snr.py').read())

# Longest duration strategy
exec(open('wrappers/run_longest_duration.py').read())
```

### **Mosaic Analysis**
```python
# Comprehensive mosaic analysis
exec(open('wrappers/run_mosaic_analysis.py').read())

# Mosaic plotting only
exec(open('wrappers/run_mosaic_plots.py').read())
```

### **Advanced Features**
```python
# Quarterly analysis
exec(open('wrappers/run_quarters.py').read())

# Full plotting suite
exec(open('wrappers/run_with_plots.py').read())

# Telescope analysis
exec(open('wrappers/run_telescope_analysis.py').read())
```

---

## ⚠️ **Known Limitations**

### **iOS Pythonista Specific**
- **Library Dependencies**: Some scientific libraries may not be available
- **Plotting Limitations**: matplotlib functionality may be restricted
- **File System Access**: Limited file system access compared to desktop
- **Performance**: Slower execution on mobile devices
- **Memory Constraints**: Large datasets may cause memory issues

### **General Mobile Limitations**
- **Screen Size**: Complex plots may be difficult to view
- **Input Methods**: Command-line arguments not directly supported
- **Background Processing**: Limited background execution capabilities
- **Network Requirements**: Some features may require internet connectivity

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```python
# Error: No module named 'numpy'
# Solution: Install required dependencies
import pip
pip.main(['install', 'numpy', 'matplotlib', 'pytz'])
```

#### **File Path Issues**
```python
# Error: File not found
# Solution: Check file paths and ensure proper directory structure
import os
print(os.getcwd())  # Check current directory
print(os.listdir('.'))  # List files
```

#### **Configuration Errors**
```python
# Error: No module named 'config.settings'
# Solution: Ensure config directory and settings.py are present
# Check that config/settings.py exists in the project structure
```

#### **Plotting Issues**
```python
# Error: matplotlib backend issues
# Solution: Try different backends or disable plotting
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

### **Performance Optimization**
```python
# Reduce memory usage
# Use report-only modes when possible
exec(open('wrappers/run_report_only.py').read())
exec(open('wrappers/run_quarters_report.py').read())

# Avoid complex plotting on mobile devices
# Use desktop for full visualization features
```

### **Debugging Tips**
```python
# Enable verbose output
import sys
sys.argv.append('--verbose')  # If supported by wrapper

# Check system capabilities
import platform
print(f"Platform: {platform.platform()}")
print(f"Python: {platform.python_version()}")

# Test individual components
try:
    import numpy
    print("✅ NumPy available")
except ImportError:
    print("❌ NumPy not available")

try:
    import matplotlib
    print("✅ Matplotlib available")
except ImportError:
    print("❌ Matplotlib not available")
```

---

## 📞 **Support**

### **Getting Help**
- **Desktop Issues**: Use main project documentation
- **Mobile-Specific Issues**: Check this mobile app documentation
- **iOS Pythonista**: Consult Pythonista documentation and forums
- **Bug Reports**: Include device info and iOS version

### **Reporting Mobile Issues**
Please include:
- iOS version and device model
- Pythonista version
- Complete error messages
- Steps to reproduce the issue
- Whether the same script works on desktop

---

## 🔄 **Future Development**

### **Planned Improvements**
- Enhanced iOS Pythonista compatibility testing
- Simplified mobile-specific interfaces
- Reduced dependency requirements
- Mobile-optimized plotting options
- Touch-friendly user interfaces

### **Contributing**
Mobile app development contributions are welcome:
- Test wrapper scripts on iOS devices
- Report compatibility issues
- Suggest mobile-specific improvements
- Help with iOS Pythonista optimization

---

**🌟 Happy Mobile Observing! 📱🔭**

*Mobile features are experimental - use desktop version for production planning*