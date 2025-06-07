# AstroScope Planner Mobile App - Complete Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [macOS Development Environment Setup](#macos-development-environment-setup)
4. [Project Setup](#project-setup)
5. [Testing the Application](#testing-the-application)
6. [iOS Development and Deployment](#ios-development-and-deployment)
7. [Android Development and Deployment](#android-development-and-deployment)
8. [App Store Deployment](#app-store-deployment)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance and Updates](#maintenance-and-updates)

## Overview

The AstroScope Planner mobile app is a comprehensive astronomy planning application built with Kivy that integrates existing astropy modules. This guide provides step-by-step instructions for setting up a development environment on macOS, testing the application, and deploying to both iOS and Android platforms.

### Key Features
- **Cross-platform compatibility** (iOS and Android)
- **Real-time trajectory and visibility plotting**
- **Comprehensive reporting system**
- **GPS location integration**
- **Mosaic planning with visualizations**
- **Touch-optimized interface**

## Prerequisites

### Hardware Requirements
- **macOS computer** (for iOS development)
- **Minimum 16GB RAM** (recommended 32GB)
- **50GB free disk space**
- **iPhone/iPad** for iOS testing
- **Android device** for Android testing

### Software Requirements
- **macOS 12.0 or later**
- **Xcode 14.0 or later**
- **Python 3.8-3.11** (Kivy compatibility)
- **Git**
- **Homebrew**

## macOS Development Environment Setup

### Step 1: Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python and Dependencies
```bash
# Install Python 3.11 (recommended for Kivy)
brew install python@3.11

# Create symbolic link
ln -sf /opt/homebrew/bin/python3.11 /usr/local/bin/python3

# Verify installation
python3 --version  # Should show Python 3.11.x
```

### Step 3: Install Xcode and Command Line Tools
```bash
# Install Xcode from App Store
# Then install command line tools
xcode-select --install

# Accept Xcode license
sudo xcodebuild -license accept
```

### Step 4: Install Java (for Android development)
```bash
# Install OpenJDK 11
brew install openjdk@11

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Step 5: Install Android SDK
```bash
# Install Android Studio
brew install --cask android-studio

# Or install SDK tools only
brew install --cask android-sdk
```

### Step 6: Set Environment Variables
Add to `~/.zshrc`:
```bash
# Android SDK
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools"

# Java
export JAVA_HOME="/opt/homebrew/opt/openjdk@11"

# iOS Development
export IOS_PLATFORM_DIR="/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform"
```

Reload environment:
```bash
source ~/.zshrc
```

## Project Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/popoloni/astropy.git
cd astropy
git checkout app  # Switch to mobile app branch
```

### Step 2: Create Python Virtual Environment
```bash
cd mobile_app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install buildozer cython

# Install iOS-specific dependencies (if targeting iOS)
pip install kivy-ios

# Install additional tools
pip install pytest black flake8
```

### Step 4: Install Kivy Dependencies (macOS)
```bash
# Install SDL2 dependencies
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer

# Install other dependencies
brew install pkg-config

# Set environment variables for Kivy
export KIVY_WINDOW=sdl2
export KIVY_GL_BACKEND=gl
```

### Step 5: Verify Installation
```bash
# Test Kivy installation
python -c "import kivy; print('Kivy version:', kivy.__version__)"

# Test app imports
python -c "from utils.app_state import AppState; print('App imports working')"
```

## Testing the Application

### Step 1: Desktop Testing
```bash
# Run the app on desktop (for initial testing)
python main.py

# Run with debug mode
KIVY_LOG_LEVEL=debug python main.py
```

### Step 2: Run Test Suite
```bash
# Run mobile app tests
python test_app.py

# Run with verbose output
python test_app.py -v
```

### Step 3: Test Individual Components
```bash
# Test plotting functionality
python -c "
from utils.plotting import mobile_plot_generator
import numpy as np
print('Testing plotting...')
# Add test code here
"

# Test astropy integration
python -c "
import sys
sys.path.append('..')
import astropy
catalog = astropy.get_combined_catalog()
print(f'Astropy integration: {len(catalog)} objects loaded')
"
```

## iOS Development and Deployment

### Step 1: Install kivy-ios
```bash
# Install kivy-ios toolchain
pip install kivy-ios

# Initialize toolchain
toolchain build python3 kivy
```

### Step 2: Create iOS Project
```bash
# Create iOS project directory
mkdir ios_build
cd ios_build

# Initialize iOS project
toolchain create AstroScope ../
```

### Step 3: Configure iOS Project
Edit `ios_build/AstroScope-ios/AstroScope.xcodeproj`:

1. **Set Bundle Identifier**: `com.yourcompany.astroscope`
2. **Set Team**: Your Apple Developer Team
3. **Set Deployment Target**: iOS 12.0 or later
4. **Configure Capabilities**:
   - Location Services
   - Background App Refresh

### Step 4: Build for iOS Simulator
```bash
# Build for simulator
toolchain build --arch x86_64 --sdk iphonesimulator

# Create Xcode project
toolchain create AstroScope ../

# Open in Xcode
open AstroScope-ios/AstroScope.xcodeproj
```

### Step 5: Build for iOS Device
```bash
# Build for device
toolchain build --arch arm64 --sdk iphoneos

# Create distribution build
toolchain create AstroScope ../ --bootstrap ios --requirements python3,kivy,numpy,matplotlib
```

### Step 6: Test on iOS Device
1. Connect iPhone/iPad via USB
2. Select device in Xcode
3. Click "Build and Run"
4. Trust developer certificate on device

### Step 7: Create iOS Archive
```bash
# In Xcode:
# 1. Product → Archive
# 2. Distribute App
# 3. Choose distribution method
```

## Android Development and Deployment

### Step 1: Configure Buildozer
The `buildozer.spec` file is already configured. Verify settings:

```ini
[app]
title = AstroScope Planner
package.name = astroscope
package.domain = com.yourcompany

[buildozer]
log_level = 2

[app]
requirements = python3,kivy,numpy,matplotlib,pandas,pytz,pillow

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
```

### Step 2: Initialize Buildozer
```bash
# Initialize buildozer (first time only)
buildozer init

# Update buildozer
buildozer android clean
```

### Step 3: Build Debug APK
```bash
# Build debug version
buildozer android debug

# This will:
# 1. Download Android SDK/NDK
# 2. Download Python-for-Android
# 3. Compile dependencies
# 4. Create APK file
```

### Step 4: Install on Android Device
```bash
# Enable USB debugging on Android device
# Connect device via USB

# Install APK
adb install bin/astroscope-0.1-arm64-v8a-debug.apk

# Or use buildozer
buildozer android deploy
```

### Step 5: Build Release APK
```bash
# Generate keystore (first time only)
keytool -genkey -v -keystore astroscope.keystore -alias astroscope -keyalg RSA -keysize 2048 -validity 10000

# Build release
buildozer android release

# Sign APK manually if needed
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore astroscope.keystore bin/astroscope-0.1-arm64-v8a-release-unsigned.apk astroscope
```

### Step 6: Test Android Build
```bash
# Run on device
buildozer android deploy run

# View logs
buildozer android logcat
```

## App Store Deployment

### iOS App Store

#### Step 1: Apple Developer Account Setup
1. **Enroll in Apple Developer Program** ($99/year)
2. **Create App ID** in Developer Portal
3. **Configure App Services**:
   - Location Services
   - Background App Refresh

#### Step 2: App Store Connect Setup
1. **Create new app** in App Store Connect
2. **Fill app information**:
   - Name: "AstroScope Planner"
   - Category: "Education" or "Utilities"
   - Keywords: "astronomy, astrophotography, telescope, planning"
3. **Upload screenshots** (required sizes):
   - iPhone 6.7": 1290×2796
   - iPhone 6.5": 1242×2688
   - iPhone 5.5": 1242×2208
   - iPad Pro 12.9": 2048×2732

#### Step 3: Create App Store Build
```bash
# In Xcode:
# 1. Product → Archive
# 2. Distribute App → App Store Connect
# 3. Upload to App Store Connect
```

#### Step 4: Submit for Review
1. **Complete app information**
2. **Add app description**:
```
AstroScope Planner is the ultimate mobile astronomy planning app for astrophotographers and amateur astronomers. Plan your observation sessions with real-time trajectory plots, visibility charts, and comprehensive mosaic planning tools.

Features:
• Real-time object tracking and visibility calculations
• Interactive trajectory and altitude plots
• Comprehensive mosaic planning with panel layouts
• GPS location integration
• Detailed observation reports
• Touch-optimized interface for mobile use
• Integration with professional astronomy catalogs

Perfect for planning deep-sky astrophotography sessions, finding optimal viewing times, and creating detailed mosaic captures of extended objects.
```
3. **Submit for review**

### Android Play Store

#### Step 1: Google Play Console Setup
1. **Create Google Play Developer account** ($25 one-time fee)
2. **Create new app** in Play Console
3. **Choose app details**:
   - App name: "AstroScope Planner"
   - Category: "Education"
   - Content rating: "Everyone"

#### Step 2: Prepare Release
```bash
# Build signed release APK
buildozer android release

# Or build AAB (recommended)
buildozer android aab
```

#### Step 3: Upload to Play Console
1. **Create new release** in Play Console
2. **Upload APK/AAB** file
3. **Add release notes**:
```
Initial release of AstroScope Planner - the comprehensive mobile astronomy planning app.

Features:
- Real-time object tracking and visibility calculations
- Interactive trajectory and altitude plots
- Comprehensive mosaic planning tools
- GPS location integration
- Detailed observation reports
- Touch-optimized mobile interface

Perfect for astrophotographers and amateur astronomers planning observation sessions.
```

#### Step 4: Store Listing
1. **Add app description** (same as iOS)
2. **Upload screenshots**:
   - Phone: 1080×1920 (minimum)
   - Tablet: 1200×1920 (minimum)
3. **Add feature graphic**: 1024×500
4. **Set content rating**
5. **Submit for review**

## Troubleshooting

### Common iOS Issues

#### Build Errors
```bash
# Clean build
rm -rf ios_build
toolchain clean

# Rebuild toolchain
toolchain build python3 kivy

# Check iOS deployment target
# Ensure iOS 12.0+ in Xcode project settings
```

#### Code Signing Issues
```bash
# Check certificates
security find-identity -v -p codesigning

# Reset provisioning profiles
# Delete profiles in Xcode → Preferences → Accounts
```

### Common Android Issues

#### Buildozer Errors
```bash
# Clean buildozer
buildozer android clean

# Update buildozer
pip install --upgrade buildozer

# Check Java version
java -version  # Should be Java 11
```

#### NDK/SDK Issues
```bash
# Set correct paths in buildozer.spec
android.sdk_path = /Users/username/Library/Android/sdk
android.ndk_path = /Users/username/Library/Android/sdk/ndk/25.2.9519653

# Download specific NDK version
sdkmanager "ndk;25.2.9519653"
```

#### Permission Issues
```bash
# Check Android permissions in buildozer.spec
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE

# Test permissions on device
adb shell pm list permissions -d -g
```

### Performance Issues

#### Memory Optimization
```python
# In main.py, add memory management
import gc

class AstroScopeApp(App):
    def on_pause(self):
        # Clean up resources when app is paused
        gc.collect()
        return True
    
    def on_resume(self):
        # Reload necessary resources
        pass
```

#### Plot Optimization
```python
# In utils/plotting.py
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Optimize figure size for mobile
fig = plt.figure(figsize=(8, 6), dpi=100)
```

## Maintenance and Updates

### Version Management
```bash
# Update version in buildozer.spec
version = 1.1

# Update version in main.py
__version__ = '1.1'

# Tag release
git tag v1.1
git push origin v1.1
```

### Dependency Updates
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Test with new dependencies
python test_app.py

# Update buildozer.spec if needed
requirements = python3,kivy==2.1.0,numpy>=1.21.0
```

### Store Updates

#### iOS Updates
1. **Increment build number** in Xcode
2. **Archive and upload** new build
3. **Submit update** in App Store Connect

#### Android Updates
1. **Increment version code** in buildozer.spec
2. **Build new release**
3. **Upload to Play Console**

### Monitoring and Analytics
```python
# Add crash reporting (optional)
try:
    import crashlytics
    crashlytics.init()
except ImportError:
    pass

# Add usage analytics (optional)
try:
    import analytics
    analytics.track('app_opened')
except ImportError:
    pass
```

## Security Considerations

### Code Obfuscation
```bash
# For sensitive algorithms, consider obfuscation
pip install pyarmor

# Obfuscate critical files
pyarmor obfuscate --recursive utils/
```

### API Keys and Secrets
```python
# Store sensitive data securely
# Use environment variables or secure storage

# For iOS: Keychain Services
# For Android: EncryptedSharedPreferences
```

### Permissions
```xml
<!-- Minimal permissions in buildozer.spec -->
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

<!-- Request permissions at runtime -->
```

## Conclusion

This guide provides comprehensive instructions for deploying the AstroScope Planner mobile app to both iOS and Android platforms. The app is now ready for production deployment with:

- ✅ **Complete development environment setup**
- ✅ **Cross-platform build configuration**
- ✅ **Store deployment procedures**
- ✅ **Troubleshooting guides**
- ✅ **Maintenance procedures**

For support or questions, refer to the project documentation or create an issue in the repository.

**Repository**: `popoloni/astropy` (branch: `app`)  
**Status**: Ready for production deployment  
**Platforms**: iOS 12.0+, Android API 21+