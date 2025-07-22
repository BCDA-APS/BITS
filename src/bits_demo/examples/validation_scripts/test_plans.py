#!/usr/bin/env python3
"""
Test Custom Plans with Simulation and Real Devices

This script tests the custom plans created in the tutorial
with both simulation mode and real devices.
"""

import sys
import time
import importlib

def test_plan_simulation():
    """Test all custom plans in simulation mode."""
    print("🧪 Testing Custom Plans (Simulation Mode)")
    print("=" * 50)
    
    try:
        # Import instrument - adjust name as needed
        instrument_names = ['my_beamline', 'my_instrument', 'demo_instrument']
        startup_module = None
        
        for name in instrument_names:
            try:
                startup_module = importlib.import_module(f"{name}.startup")
                print(f"✅ Loaded instrument: {name}")
                break
            except ImportError:
                continue
        
        if not startup_module:
            print("❌ No instrument package found")
            return False
        
        # Get RunEngine and devices
        RE = getattr(startup_module, 'RE')
        
        # Import devices - get them from the module namespace
        import bluesky.preprocessors as bpp
        motors = list(bpp._devices_by_label.get('motors', []))
        detectors = list(bpp._devices_by_label.get('detectors', []))
        
        if not (motors and detectors):
            print("❌ No motors or detectors available")
            return False
        
        # Enable simulation mode
        original_mode = getattr(RE, 'simulate_mode', False)
        RE.simulate_mode = True
        
        print(f"Using motor: {motors[0].name}, detector: {detectors[0].name}")
        
        try:
            # Import custom plans
            plans_module = importlib.import_module(f"{startup_module.__name__.split('.')[0]}.plans.custom_plans")
            
            # Test each custom plan
            plans_to_test = [
                ('motor_characterization', plans_module.motor_characterization, 
                 (motors[0], detectors[0]), {'num_points': 5}),
                 
                ('quick_scan', plans_module.quick_scan,
                 (motors[0], detectors[0]), {'range_pm': 0.5, 'points': 5}),
                 
                ('detector_optimization', plans_module.detector_optimization,
                 (motors[0], detectors[0]), {'initial_range': 1.0, 'refinement_cycles': 1})
            ]
            
            # Test sample_alignment if we have multiple motors
            if len(motors) >= 2:
                plans_to_test.append(
                    ('sample_alignment', plans_module.sample_alignment,
                     (motors[:2], detectors[0]), {'scan_range': 1.0, 'step_size': 0.2})
                )
            
            successful_plans = 0
            
            for plan_name, plan_func, args, kwargs in plans_to_test:
                try:
                    print(f"Testing {plan_name}...")
                    RE(plan_func(*args, **kwargs))
                    print(f"  ✅ {plan_name} completed successfully")
                    successful_plans += 1
                except Exception as e:
                    print(f"  ❌ {plan_name} failed: {e}")
            
            print(f"\n📊 Simulation Results: {successful_plans}/{len(plans_to_test)} plans passed")
            return successful_plans == len(plans_to_test)
            
        except ImportError:
            print("❌ Custom plans module not found")
            return False
        finally:
            # Restore original simulation mode
            RE.simulate_mode = original_mode
            
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        return False

def test_plan_execution():
    """Test plans with real devices (small safe moves)."""
    print("\n🔧 Testing Custom Plans (Real Devices)")
    print("=" * 50)
    
    try:
        # Import instrument
        instrument_names = ['my_beamline', 'my_instrument', 'demo_instrument']
        startup_module = None
        
        for name in instrument_names:
            try:
                startup_module = importlib.import_module(f"{name}.startup")
                break
            except ImportError:
                continue
        
        if not startup_module:
            print("❌ No instrument package found")
            return False
        
        # Get RunEngine and devices
        RE = getattr(startup_module, 'RE')
        
        import bluesky.preprocessors as bpp
        motors = list(bpp._devices_by_label.get('motors', []))
        detectors = list(bpp._devices_by_label.get('detectors', []))
        
        if not (motors and detectors):
            print("❌ No motors or detectors available")
            return False
        
        # Test device connectivity first
        motor = motors[0]
        detector = detectors[0]
        
        try:
            motor_pos = motor.position
            detector_connected = detector.connected
            
            if not detector_connected:
                print(f"❌ Detector {detector.name} not connected")
                return False
                
            print(f"✅ Motor {motor.name} at position {motor_pos:.3f}")
            print(f"✅ Detector {detector.name} connected")
            
        except Exception as e:
            print(f"❌ Device connectivity test failed: {e}")
            return False
        
        try:
            # Import custom plans
            plans_module = importlib.import_module(f"{startup_module.__name__.split('.')[0]}.plans.custom_plans")
            
            # Test safe plans with real devices
            safe_tests = [
                ('quick_scan (small)', plans_module.quick_scan,
                 (motor, detector), {'range_pm': 0.1, 'points': 5}),
                 
                ('motor_characterization (small range)', plans_module.motor_characterization,
                 (motor, detector), {'range_fraction': 0.05, 'num_points': 5})
            ]
            
            successful_tests = 0
            
            for test_name, plan_func, args, kwargs in safe_tests:
                try:
                    print(f"Executing {test_name}...")
                    initial_pos = motor.position
                    
                    RE(plan_func(*args, **kwargs))
                    
                    final_pos = motor.position
                    print(f"  ✅ {test_name} completed")
                    print(f"     Motor moved from {initial_pos:.3f} to {final_pos:.3f}")
                    successful_tests += 1
                    
                    # Brief pause between tests
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  ❌ {test_name} failed: {e}")
            
            print(f"\n📊 Real Device Results: {successful_tests}/{len(safe_tests)} tests passed")
            return successful_tests == len(safe_tests)
            
        except ImportError:
            print("❌ Custom plans module not found")
            return False
            
    except Exception as e:
        print(f"❌ Real device test failed: {e}")
        return False

def test_built_in_plans():
    """Test built-in Bluesky plans work with our devices."""
    print("\n📚 Testing Built-in Plans")
    print("=" * 50)
    
    try:
        # Import instrument
        instrument_names = ['my_beamline', 'my_instrument', 'demo_instrument']  
        startup_module = None
        
        for name in instrument_names:
            try:
                startup_module = importlib.import_module(f"{name}.startup")
                break
            except ImportError:
                continue
        
        if not startup_module:
            print("❌ No instrument package found")
            return False
        
        # Get RunEngine and devices
        RE = getattr(startup_module, 'RE')
        
        import bluesky.plans as bp
        import bluesky.preprocessors as bpp
        
        motors = list(bpp._devices_by_label.get('motors', []))
        detectors = list(bpp._devices_by_label.get('detectors', []))
        
        if not (motors and detectors):
            print("❌ No motors or detectors available")
            return False
        
        motor = motors[0]
        detector = detectors[0]
        
        # Test built-in plans
        built_in_tests = [
            ('count', bp.count, ([detector],), {'num': 1}),
            ('rel_scan', bp.rel_scan, ([detector], motor, -0.1, 0.1, 5), {}),
            ('scan', bp.scan, ([detector], motor, motor.position - 0.1, motor.position + 0.1, 5), {})
        ]
        
        successful_tests = 0
        
        for test_name, plan_func, args, kwargs in built_in_tests:
            try:
                print(f"Testing {test_name}...")
                RE(plan_func(*args, **kwargs))
                print(f"  ✅ {test_name} completed successfully")
                successful_tests += 1
                
                time.sleep(0.5)  # Brief pause
                
            except Exception as e:
                print(f"  ❌ {test_name} failed: {e}")
        
        print(f"\n📊 Built-in Plans: {successful_tests}/{len(built_in_tests)} tests passed")
        return successful_tests == len(built_in_tests)
        
    except Exception as e:
        print(f"❌ Built-in plans test failed: {e}")
        return False

def main():
    """Run all plan tests."""
    print("🧪 BITS Custom Plan Testing Suite")
    print("=" * 60)
    
    tests = [
        ("Plan Simulation", test_plan_simulation),
        ("Built-in Plans", test_built_in_plans),
        ("Real Device Plans", test_plan_execution)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Plan Testing Results")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:<20}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} test suites passed")
    
    if passed == len(results):
        print("🎉 All plan tests passed! Your custom plans are working correctly.")
        return 0
    else:
        print("⚠️  Some plan tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())