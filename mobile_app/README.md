# AstroScope Planner Mobile App

A Kivy-based mobile application for astrophotography planning that integrates the powerful astropy calculation engine.

## Features

- **Tonight's Targets**: View optimized list of observable targets for your location
- **Target Details**: Detailed information including visibility windows, imaging recommendations, and technical data
- **Mosaic Planning**: Plan complex mosaic imaging projects with automatic panel calculation
- **Multiple Strategies**: Choose from 6 different scheduling strategies
- **Location Management**: GPS support and saved location profiles
- **Cross-Platform**: Runs on Android, iOS, and desktop platforms

## Installation

### Development Setup

1. Install Python 3.8+ and pip
2. Install Kivy and dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

### Building for Android

1. Install Buildozer:
   ```bash
   pip install buildozer
   ```
2. Initialize and build:
   ```bash
   buildozer android debug
   ```

### Building for iOS

1. Install kivy-ios:
   ```bash
   pip install kivy-ios
   ```
2. Build dependencies:
   ```bash
   toolchain build python3 kivy
   ```
3. Create Xcode project:
   ```bash
   toolchain create AstroScope .
   ```

## Architecture

The app is built with a modular architecture:

- **main.py**: Main application entry point
- **screens/**: Individual screen implementations
  - `home_screen.py`: Dashboard and overview
  - `targets_screen.py`: Target browsing and filtering
  - `target_detail_screen.py`: Detailed target information
  - `mosaic_screen.py`: Mosaic planning interface
  - `settings_screen.py`: Configuration and preferences
- **utils/**: Utility modules
  - `app_state.py`: Centralized state management
  - `location_manager.py`: GPS and location handling
- **widgets/**: Custom UI components
- **assets/**: Images, icons, and resources

## Integration with AstroScope Engine

The mobile app seamlessly integrates with the existing astropy modules:

- **astronomy/**: Core astronomical calculations
- **analysis/**: Target scoring and optimization
- **catalogs/**: Object catalog management
- **models/**: Data models and scheduling strategies
- **config/**: Configuration management
- **utilities/**: Helper functions
- **visualization/**: Data visualization

## Configuration

The app uses the same configuration system as the desktop version:

- Location profiles from `config.json`
- Telescope configurations
- Scheduling preferences
- Imaging parameters

## Usage

1. **Set Location**: Configure your observing location in Settings
2. **Choose Strategy**: Select a scheduling strategy that fits your goals
3. **Browse Targets**: View tonight's optimized target list
4. **Plan Session**: Add targets to your observation plan
5. **Mosaic Planning**: Use the mosaic planner for large objects

## Supported Platforms

- **Android**: API 21+ (Android 5.0+)
- **iOS**: iOS 10.0+
- **Desktop**: Windows, macOS, Linux

## Dependencies

- Kivy 2.1.0+ (UI framework)
- NumPy (numerical calculations)
- Matplotlib (plotting and visualization)
- PyTZ (timezone handling)
- Pandas (data manipulation)
- Pillow (image processing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on target platforms
5. Submit a pull request

## License

This project is part of the AstroScope suite and follows the same licensing terms.

## Support

For support, bug reports, or feature requests, please use the GitHub issue tracker or contact the development team.