#!/usr/bin/env python3
"""
Complete Setup Validation for BITS Tutorial

This script validates the entire BITS setup from IOCs to working plans.
Run this after completing each tutorial step to ensure everything is working.
"""

import sys
import subprocess
import importlib.util
import time
import os
from pathlib import Path

def check_ioc_containers():
    """Check if demo IOCs are running."""
    print("🔍 Checking IOC Containers...")
    
    try:
        # Check if containers are running
        result = subprocess.run(['podman', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Cannot run podman command")
            return False
            
        containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        required_containers = ['adsim_ioc', 'gp_ioc']
        running_containers = []
        
        for container in required_containers:
            if container in containers:
                print(f"  ✅ {container}: Running")
                running_containers.append(container)
            else:
                print(f"  ❌ {container}: Not running")
        
        if len(running_containers) == len(required_containers):
            print("✅ All required IOCs are running")
            return True
        else:
            print(f"❌ {len(running_containers)}/{len(required_containers)} IOCs running")
            print("Run: ./scripts/start_demo_iocs.sh")
            return False
            
    except FileNotFoundError:
        print("❌ Podman not found - cannot check container status")
        return False
    except Exception as e:
        print(f"❌ Error checking containers: {e}")
        return False

def check_python_environment():
    """Check Python environment and BITS installation."""
    print("\n🐍 Checking Python Environment...")
    
    required_packages = [
        ('bluesky', 'Bluesky framework'),
        ('ophyd', 'OPHYD device library'), 
        ('databroker', 'Data management'),
        ('apsbits', 'BITS framework')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                print(f"  ❌ {package}: Not installed ({description})")
                missing_packages.append(package)
            else:
                # Try to import and get version
                try:
                    module = importlib.import_module(package)
                    version = getattr(module, '__version__', 'unknown')
                    print(f"  ✅ {package}: {version} ({description})")
                except Exception as e:
                    print(f"  ⚠️  {package}: Import error - {e}")
        except Exception as e:
            print(f"  ❌ {package}: Check failed - {e}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install apsbits")
        return False
    else:
        print("✅ All required packages installed")
        return True

def check_instrument_package():
    """Check if instrument package is installed and working."""
    print("\n📦 Checking Instrument Package...")
    
    # Check if any instrument package exists
    possible_names = ['my_beamline', 'my_instrument', 'demo_instrument']
    instrument_name = None
    
    for name in possible_names:
        try:
            spec = importlib.util.find_spec(name)
            if spec is not None:
                instrument_name = name
                print(f"  ✅ Found instrument package: {name}")
                break
        except:
            continue
    
    if not instrument_name:
        print("  ❌ No instrument package found")
        print("  Run: create-bits my_beamline && pip install -e .")
        return False
    
    # Try to import startup module
    try:
        startup_module = f"{instrument_name}.startup"
        spec = importlib.util.find_spec(startup_module)
        if spec is None:
            print(f"  ❌ Startup module not found: {startup_module}")
            return False
        else:
            print(f"  ✅ Startup module available: {startup_module}")
    except Exception as e:
        print(f"  ❌ Error checking startup module: {e}")
        return False
    
    # Check configuration files
    config_files = ['iconfig.yml', 'devices.yml']
    package_path = Path(spec.origin).parent / 'configs'
    
    for config_file in config_files:
        config_path = package_path / config_file
        if config_path.exists():
            print(f"  ✅ Configuration file: {config_file}")
        else:
            print(f"  ❌ Missing configuration: {config_file}")
    
    return True

def test_epics_connectivity():
    """Test EPICS connectivity to demo IOCs."""
    print("\n📡 Testing EPICS Connectivity...")
    
    try:
        import epics
    except ImportError:
        print("  ⚠️  PyEPICS not available - skipping connectivity test")
        return True  # Not critical for basic functionality
    
    test_pvs = [
        ('gp:m1.DESC', 'GP IOC motor description'),
        ('gp:scaler1.DESC', 'GP IOC scaler description'),
        ('adsim:cam1:Acquire', 'Area detector acquisition PV')
    ]
    
    connected_pvs = 0
    
    for pv_name, description in test_pvs:
        try:
            pv = epics.PV(pv_name)
            if pv.wait_for_connection(timeout=5.0):
                value = pv.get()
                print(f"  ✅ {pv_name}: {value}")
                connected_pvs += 1
            else:
                print(f"  ❌ {pv_name}: Connection timeout")
        except Exception as e:
            print(f"  ❌ {pv_name}: Error - {e}")
    
    if connected_pvs == len(test_pvs):
        print("✅ All test PVs connected successfully")
        return True
    else:
        print(f"❌ {connected_pvs}/{len(test_pvs)} PVs connected")
        print("Check IOC status and EPICS environment")
        return False

def test_instrument_loading():
    """Test instrument loading and basic functionality."""
    print("\n🔬 Testing Instrument Loading...")
    
    # Find instrument package
    possible_names = ['my_beamline', 'my_instrument', 'demo_instrument']
    instrument_name = None
    
    for name in possible_names:
        try:
            spec = importlib.util.find_spec(name)
            if spec is not None:
                instrument_name = name
                break
        except:
            continue
    
    if not instrument_name:
        print("  ❌ No instrument package found")
        return False
    
    try:
        # Import the startup module
        print(f"  Loading {instrument_name}.startup...")
        startup_module = importlib.import_module(f"{instrument_name}.startup")
        
        # Check for key objects
        required_objects = ['RE', 'cat']  # RunEngine and catalog
        missing_objects = []
        
        for obj_name in required_objects:
            if hasattr(startup_module, obj_name):
                obj = getattr(startup_module, obj_name)
                print(f"  ✅ {obj_name}: {type(obj)}")
            else:
                print(f"  ❌ {obj_name}: Not found")
                missing_objects.append(obj_name)
        
        if missing_objects:
            print(f"❌ Missing objects: {', '.join(missing_objects)}")
            return False
        
        # Test RunEngine state
        RE = getattr(startup_module, 'RE')
        if hasattr(RE, 'state'):
            print(f"  ✅ RunEngine state: {RE.state}")
        
        print("✅ Instrument loaded successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading instrument: {e}")
        return False

def test_device_functionality():
    """Test basic device operations."""
    print("\n🔧 Testing Device Functionality...")
    
    # Find instrument package
    possible_names = ['my_beamline', 'my_instrument', 'demo_instrument']
    instrument_name = None
    
    for name in possible_names:
        try:
            spec = importlib.util.find_spec(name)
            if spec is not None:
                instrument_name = name
                break
        except:
            continue
    
    if not instrument_name:
        print("  ❌ No instrument package found")
        return False
    
    try:
        # Import startup and test devices
        startup_module = importlib.import_module(f"{instrument_name}.startup")
        
        # Get RunEngine
        RE = getattr(startup_module, 'RE')
        
        # Import bluesky plans
        import bluesky.plans as bp
        import bluesky.preprocessors as bpp
        
        # Try to get device lists
        try:
            motors = list(bpp._devices_by_label.get('motors', []))
            detectors = list(bpp._devices_by_label.get('detectors', []))
            
            print(f"  Found {len(motors)} motors, {len(detectors)} detectors")
            
            if motors and detectors:
                # Test a simple count
                print("  Testing simple count...")
                RE(bp.count([detectors[0]], num=1))
                print("  ✅ Simple count successful")
                
                # Test motor position reading
                print("  Testing motor position reading...")
                motor = motors[0]
                position = motor.position
                print(f"  ✅ Motor {motor.name} position: {position}")
                
                return True
            else:
                print("  ❌ No motors or detectors available")
                return False
                
        except Exception as e:
            print(f"  ❌ Error testing devices: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error setting up device test: {e}")
        return False

def test_data_collection():
    """Test data collection and catalog functionality."""
    print("\n📊 Testing Data Collection...")
    
    # Find instrument package  
    possible_names = ['my_beamline', 'my_instrument', 'demo_instrument']
    instrument_name = None
    
    for name in possible_names:
        try:
            spec = importlib.util.find_spec(name)
            if spec is not None:
                instrument_name = name
                break
        except:
            continue
    
    if not instrument_name:
        print("  ❌ No instrument package found")
        return False
    
    try:
        # Import startup
        startup_module = importlib.import_module(f"{instrument_name}.startup")
        
        RE = getattr(startup_module, 'RE')
        cat = getattr(startup_module, 'cat')
        
        # Count initial runs
        initial_runs = len(list(cat))
        print(f"  Initial runs in catalog: {initial_runs}")
        
        # Import devices and plans
        import bluesky.plans as bp
        import bluesky.preprocessors as bpp
        
        # Get devices
        detectors = list(bpp._devices_by_label.get('detectors', []))
        
        if not detectors:
            print("  ❌ No detectors available for testing")
            return False
        
        # Perform a simple measurement
        print("  Performing test measurement...")
        RE(bp.count([detectors[0]], num=1))
        
        # Check if run was saved
        final_runs = len(list(cat))
        new_runs = final_runs - initial_runs
        
        if new_runs > 0:
            print(f"  ✅ {new_runs} new run(s) saved to catalog")
            
            # Try to read the latest run
            latest_run = cat[-1]
            scan_id = latest_run.metadata['start']['scan_id']
            print(f"  ✅ Latest run scan_id: {scan_id}")
            
            return True
        else:
            print("  ❌ No new runs found in catalog")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing data collection: {e}")
        return False

def generate_summary_report():
    """Generate a summary report of the validation."""
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY REPORT")
    print("=" * 60)
    
    tests = [
        ("IOC Containers", check_ioc_containers),
        ("Python Environment", check_python_environment),
        ("Instrument Package", check_instrument_package),
        ("EPICS Connectivity", test_epics_connectivity),
        ("Instrument Loading", test_instrument_loading),
        ("Device Functionality", test_device_functionality),
        ("Data Collection", test_data_collection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print results
    print("\n📊 Test Results:")
    print("-" * 40)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:<20}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall Score: {passed}/{len(results)} tests passed")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if passed == len(results):
        print("  🎉 Perfect! Your BITS setup is working correctly.")
        print("  Ready to proceed with the tutorial or start real measurements.")
    elif passed >= len(results) * 0.8:
        print("  🟡 Good setup with minor issues.")
        print("  Review failed tests and address any critical issues.")
    else:
        print("  🔴 Setup needs attention.")
        print("  Address failed tests before proceeding with measurements.")
    
    # Next steps
    failed_tests = [name for name, success in results if not success]
    if failed_tests:
        print(f"\n🔧 Failed Tests to Address: {', '.join(failed_tests)}")
    
    return passed == len(results)

def main():
    """Run complete validation."""
    print("🧪 BITS Tutorial Setup Validation")
    print("=" * 60)
    print("This script validates your complete BITS setup.")
    print("Run this after each tutorial step to ensure everything works.")
    print()
    
    success = generate_summary_report()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 VALIDATION COMPLETE: All systems operational!")
        sys.exit(0)
    else:
        print("⚠️  VALIDATION ISSUES: Some systems need attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()