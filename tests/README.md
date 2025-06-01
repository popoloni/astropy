# Astropy Test Suite

This directory contains the comprehensive test suite for the astropy astronomical calculation system.

## Directory Structure

```
tests/
├── __init__.py                 # Test suite documentation
├── README.md                   # This file
├── run_tests.py               # Legacy test runner (comprehensive integration test)
├── test_runner.py             # New comprehensive test runner
├── integration/               # End-to-end integration tests
│   ├── comprehensive_test.py
│   ├── comprehensive_test_pythonista.py
│   ├── run_test_simulation.py
│   ├── test_astropy_params.py
│   ├── test_comprehensive.py
│   ├── test_high_precision_verification.py
│   └── test_precision_integration.py
├── unit/                      # Unit tests for individual components
│   ├── test_phase3_simple.py
│   └── test_yellow_labels.py
├── precision/                 # High-precision calculation tests
│   ├── test_config.py
│   ├── test_high_precision.py
│   ├── test_phase2_functions.py
│   └── test_phase3_functions.py
├── legacy/                    # Legacy functionality tests
│   └── test_mosaic_integration.py
└── utilities/                 # Test utility functions (empty)
```

## Test Categories

### Integration Tests (`integration/`)
End-to-end tests that verify the complete system functionality:
- **test_astropy_params.py**: Tests all major parameter combinations
- **test_high_precision_verification.py**: Verifies high-precision calculations
- **test_precision_integration.py**: Tests precision system integration
- **comprehensive_test.py**: Main comprehensive integration test

### Unit Tests (`unit/`)
Tests for individual components and features:
- **test_phase3_simple.py**: Basic Phase 3 component tests
- **test_yellow_labels.py**: Yellow label feature tests

### Precision Tests (`precision/`)
Tests for high-precision astronomical calculations:
- **test_high_precision.py**: Core high-precision calculation tests
- **test_config.py**: Precision configuration management tests
- **test_phase2_functions.py**: Phase 2 precision function tests
- **test_phase3_functions.py**: Phase 3 precision function tests

### Legacy Tests (`legacy/`)
Tests for legacy functionality and backwards compatibility:
- **test_mosaic_integration.py**: Legacy mosaic integration tests

## Running Tests

### Quick Test (Recommended)
```bash
# Run the comprehensive integration test
python tests/run_tests.py
```

### Full Test Suite
```bash
# Run all test categories with detailed reporting
python tests/test_runner.py
```

### Individual Test Categories
```bash
# Run specific test files
python tests/unit/test_phase3_simple.py
python tests/integration/test_astropy_params.py
python tests/precision/test_high_precision.py
```

## Test Requirements

Most tests run with standard Python libraries. Some precision tests require:
- `pytest` (for advanced test features)
- `pytz` (for timezone handling)

## Test Results

All tests have been verified to work correctly after the reorganization:
- ✅ Unit tests: Working
- ✅ Integration tests: Working  
- ✅ Precision tests: Working (some require pytest)
- ✅ Legacy tests: Working
- ✅ Import paths: Fixed and verified
- ✅ Main astropy.py functionality: Preserved

## Adding New Tests

When adding new tests:
1. Choose the appropriate category directory
2. Follow the naming convention `test_*.py`
3. Add proper path setup for imports:
   ```python
   import sys
   import os
   # Add astropy root directory to path
   sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
   ```
4. Update the test runner if needed

## Migration Notes

This test suite was reorganized from scattered test files throughout the repository:
- All test files moved from root/utilities/legacy/wrappers to organized subdirectories
- Import paths updated for new structure
- Test runners updated to work with new organization
- All functionality preserved and verified