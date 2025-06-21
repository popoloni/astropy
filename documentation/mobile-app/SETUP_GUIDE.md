# 📱 iOS Pythonista Setup Guide

**Step-by-step guide for setting up astronomical observation planning on iOS devices using Pythonista**

> **✅ Current Mobile Solution**: This guide covers the iOS Pythonista implementation - the current working mobile solution. Wrapper scripts eliminate the need to type command-line parameters, making mobile usage practical and efficient.
> 
> **🧪 Note**: A separate experimental native mobile app is in development but not covered in this guide.

---

## 📋 **Prerequisites**

### **iOS Device Requirements**
- iOS 12.0 or later
- At least 2GB available storage
- Stable internet connection for setup
- Pythonista 3 app (paid app from App Store)

### **Knowledge Requirements**
- Basic familiarity with Python
- Understanding of file management on iOS
- Basic astronomy knowledge helpful but not required

---

## 🚀 **Quick Start Guide**

### **Step 1: Install Pythonista**
1. Open App Store on your iOS device
2. Search for "Pythonista 3"
3. Purchase and install the app (~$10 USD)
4. Launch Pythonista to verify installation

### **Step 2: Get the Project Files**
Choose one of these methods:

#### **Method A: Direct Download (Recommended)**
```python
# In Pythonista console
import requests
import zipfile
import os

# Download project (replace with actual download URL)
# Note: You'll need to get files from your desktop first
```

#### **Method B: Cloud Storage**
1. Upload project files to iCloud Drive, Dropbox, or Google Drive
2. Use Pythonista's file import feature
3. Navigate to Files app and import to Pythonista

#### **Method C: Manual Transfer**
1. Use iTunes file sharing (if available)
2. Transfer files via AirDrop from Mac
3. Use Pythonista's built-in file transfer features

### **Step 3: Install Dependencies**
```python
# In Pythonista console
import pip

# Install required packages
pip.main(['install', 'numpy'])
pip.main(['install', 'matplotlib'])  
pip.main(['install', 'pytz'])

# Verify installations
import numpy
import matplotlib
import pytz
print("✅ All dependencies installed successfully!")
```

### **Step 4: Test Basic Functionality**
```python
# Test simple wrapper script
exec(open('wrappers/run_report_only.py').read())
```

---

## 🔧 **Detailed Setup Instructions**

### **File Structure Setup**
Ensure your Pythonista directory has this structure:
```
Pythonista/
├── astropy/
│   ├── astronightplanner.py
│   ├── config/
│   │   └── settings.py
│   ├── astronomy/
│   ├── analysis/
│   ├── catalogs/
│   ├── models/
│   ├── utilities/
│   ├── visualization/
│   └── wrappers/
│       ├── run_report_only.py
│       ├── run_max_objects.py
│       └── ... (other wrapper scripts)
```

### **Configuration Setup**
1. **Create config.json**:
```json
{
  "locations": {
    "mobile_location": {
      "name": "My Location",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "timezone": "America/New_York",
      "min_altitude": 20,
      "max_altitude": 80,
      "default": true
    }
  },
  "imaging": {
    "scope": {
      "name": "Mobile Setup",
      "fov_width": 2.4,
      "fov_height": 1.8,
      "single_exposure": 10,
      "min_snr": 20
    }
  }
}
```

2. **Update location coordinates**:
   - Use GPS coordinates for your observing location
   - Set appropriate timezone
   - Adjust altitude limits based on your horizon

### **Dependency Management**
```python
# Check what's available
def check_dependencies():
    deps = ['numpy', 'matplotlib', 'pytz', 'json', 'datetime', 'os', 'sys']
    available = []
    missing = []
    
    for dep in deps:
        try:
            __import__(dep)
            available.append(dep)
        except ImportError:
            missing.append(dep)
    
    print(f"✅ Available: {available}")
    print(f"❌ Missing: {missing}")
    return missing

# Install missing dependencies
missing = check_dependencies()
if missing:
    import pip
    for dep in missing:
        if dep in ['numpy', 'matplotlib', 'pytz']:
            pip.main(['install', dep])
```

---

## 📱 **Usage Examples**

### **Basic Report Generation**
```python
# Change to project directory
import os
os.chdir('astropy')

# Run basic report
exec(open('wrappers/run_report_only.py').read())
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

### **Advanced Features**
```python
# Mosaic analysis (may be slow on mobile)
exec(open('wrappers/run_mosaic_analysis.py').read())

# Quarterly analysis
exec(open('wrappers/run_quarters_report.py').read())  # No plots version

# Telescope analysis
exec(open('wrappers/run_telescope_analysis.py').read())
```

### **Creating Custom Scripts**
```python
# Create a mobile-optimized script
def mobile_observation_report():
    """Generate a simple observation report optimized for mobile"""
    try:
        # Import required modules
        import sys
        sys.path.append('.')
        
        from config import settings
        from analysis import generate_observation_schedule
        
        # Generate report
        print("📱 Mobile Observation Report")
        print("=" * 30)
        
        # Add your custom logic here
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Try using desktop version for full functionality")

# Run custom script
mobile_observation_report()
```

---

## ⚠️ **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```python
# Error: No module named 'numpy'
# Solution:
import pip
pip.main(['install', 'numpy'])

# Error: No module named 'config.settings'  
# Solution: Check file structure and ensure config/ directory exists
import os
print(os.listdir('.'))  # Check current directory contents
```

#### **File Path Issues**
```python
# Error: File not found
# Solution: Check current directory and file paths
import os
print(f"Current directory: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# Change to correct directory
os.chdir('astropy')
```

#### **Memory Issues**
```python
# Error: Memory error or app crashes
# Solution: Use simpler scripts
exec(open('wrappers/run_report_only.py').read())  # Lighter version
# Avoid complex plotting scripts on older devices
```

#### **Matplotlib Issues**
```python
# Error: matplotlib backend issues
# Solution: Configure backend
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Or disable plotting entirely
import matplotlib
matplotlib.pyplot.ioff()  # Turn off interactive mode
```

### **Performance Optimization**

#### **For Older Devices**
```python
# Use report-only versions
exec(open('wrappers/run_report_only.py').read())
exec(open('wrappers/run_quarters_report.py').read())

# Avoid memory-intensive operations
# Skip complex plotting when possible
```

#### **For Better Performance**
```python
# Close Pythonista and restart between heavy operations
# Clear variables when done
del large_variables
import gc
gc.collect()
```

### **Debugging Tips**
```python
# Check system info
import platform
print(f"Platform: {platform.platform()}")
print(f"Python: {platform.python_version()}")

# Check available memory (if possible)
import sys
print(f"Python path: {sys.path}")

# Test individual components
try:
    from astronomy import celestial
    print("✅ Astronomy module works")
except Exception as e:
    print(f"❌ Astronomy module error: {e}")
```

---

## 📊 **Performance Expectations**

### **Expected Performance on iOS**
- **iPhone 12 or newer**: Good performance for most features
- **iPhone 8-11**: Moderate performance, avoid complex plotting
- **iPhone 7 or older**: Basic functionality only, use report-only scripts

### **Execution Times (Estimated)**
- **run_report_only.py**: 5-10 seconds
- **run_max_objects.py**: 10-20 seconds  
- **run_mosaic_analysis.py**: 30-60 seconds (may timeout)
- **Complex plotting**: May not work on older devices

### **Memory Usage**
- **Basic reports**: ~100-200MB
- **With plotting**: ~300-500MB
- **Complex analysis**: ~500MB+ (may cause crashes)

---

## 🔄 **Best Practices**

### **Mobile-Specific Recommendations**
1. **Start Simple**: Begin with `run_report_only.py`
2. **Test Incrementally**: Try one feature at a time
3. **Save Work**: Export results before trying complex operations
4. **Use WiFi**: Ensure stable internet for setup
5. **Keep Backups**: Save working configurations

### **Workflow Suggestions**
1. **Planning Phase**: Use mobile for quick checks and basic reports
2. **Detailed Analysis**: Use desktop for complex plotting and analysis
3. **Field Use**: Mobile for quick reference and basic planning
4. **Data Export**: Transfer results between devices as needed

### **Battery Management**
- Close other apps during intensive operations
- Use low power mode if available
- Keep device plugged in for long operations

---

## 🆕 **Future Improvements**

### **Planned Mobile Features**
- Simplified mobile-specific interfaces
- Touch-optimized controls
- Reduced dependency requirements
- Mobile-specific plotting options
- Offline capability improvements

### **Contributing to Mobile Development**
- Test features on your iOS device
- Report compatibility issues
- Suggest mobile-specific improvements
- Help optimize performance

---

## 📞 **Getting Help**

### **Support Resources**
- **Main Documentation**: `documentation/` folder
- **Mobile-Specific**: This mobile app documentation
- **Pythonista Help**: Pythonista app documentation
- **Community**: iOS astronomy app communities

### **Reporting Mobile Issues**
Include in your report:
- iOS version and device model
- Pythonista version
- Complete error messages
- Steps to reproduce
- Whether it works on desktop

---

**📱 Happy Mobile Observing! 🔭**

*Remember: Mobile features are experimental - use desktop for production planning*