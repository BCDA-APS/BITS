#!/usr/bin/env python3
"""
Device Testing and Validation Script for BITS Tutorial

This script tests device connectivity and functionality
for the demo IOC configuration.
"""

import sys
import time
from pathlib import Path

def test_device_connectivity():
    """Test basic device connectivity."""
    print("🔧 Device Connectivity Test")
    print("=" * 50)
    
    try:
        # Import the instrument
        # Note: Adjust import based on actual instrument name
        print("Loading instrument...")
        exec("from my_beamline.startup import *", globals())
        print("✅ Instrument loaded successfully\n")
        
        # Get device lists by label
        import bluesky.preprocessors as bpp
        
        # Test motors
        motors = list(bpp._devices_by_label.get('motors', []))
        print(f"🚗 Testing Motors ({len(motors)}):")
        motor_results = {}
        
        for motor in motors:
            try:
                # Test basic properties
                pos = motor.position
                limits = motor.limits
                connected = motor.connected
                
                motor_results[motor.name] = {
                    'connected': connected,
                    'position': pos,
                    'limits': limits,
                    'status': '✅' if connected else '❌'
                }
                
                print(f"  {motor_results[motor.name]['status']} {motor.name:<12}: "
                      f"pos={pos:8.3f}, limits={limits}, connected={connected}")
                      
            except Exception as e:
                motor_results[motor.name] = {
                    'status': '❌',
                    'error': str(e)
                }
                print(f"  ❌ {motor.name:<12}: Error - {e}")
        
        # Test detectors
        detectors = list(bpp._devices_by_label.get('detectors', []))
        print(f"\n🔍 Testing Detectors ({len(detectors)}):")
        detector_results = {}
        
        for det in detectors:
            try:
                connected = det.connected
                detector_results[det.name] = {
                    'connected': connected,
                    'status': '✅' if connected else '❌'
                }
                
                # Additional tests based on detector type
                if hasattr(det, 'channels'):  # Scaler
                    channels = det.channels
                    print(f"  {'✅' if connected else '❌'} {det.name:<12}: "
                          f"connected={connected}, channels={channels}")
                elif hasattr(det, 'cam'):  # Area detector
                    try:
                        array_size = det.cam.array_size.get()
                        print(f"  {'✅' if connected else '❌'} {det.name:<12}: "
                              f"connected={connected}, size={array_size}")
                    except:
                        print(f"  {'✅' if connected else '❌'} {det.name:<12}: "
                              f"connected={connected}")
                else:
                    print(f"  {'✅' if connected else '❌'} {det.name:<12}: "
                          f"connected={connected}")
                          
            except Exception as e:
                detector_results[det.name] = {
                    'status': '❌',
                    'error': str(e)
                }
                print(f"  ❌ {det.name:<12}: Error - {e}")
        
        # Test baseline devices
        baseline = list(bpp._devices_by_label.get('baseline', []))
        print(f"\n📊 Testing Baseline Devices ({len(baseline)}):")
        baseline_results = {}
        
        for dev in baseline:
            try:
                value = dev.get()
                connected = dev.connected
                baseline_results[dev.name] = {
                    'connected': connected,
                    'value': value,
                    'status': '✅' if connected else '❌'
                }
                print(f"  {'✅' if connected else '❌'} {dev.name:<12}: {value}")
                
            except Exception as e:
                baseline_results[dev.name] = {
                    'status': '❌',
                    'error': str(e)
                }
                print(f"  ❌ {dev.name:<12}: Error - {e}")
        
        # Summary
        print(f"\n📋 Test Summary:")
        total_motors = len(motors)
        connected_motors = sum(1 for r in motor_results.values() if r.get('connected', False))
        print(f"  Motors:    {connected_motors}/{total_motors} connected")
        
        total_detectors = len(detectors)
        connected_detectors = sum(1 for r in detector_results.values() if r.get('connected', False))
        print(f"  Detectors: {connected_detectors}/{total_detectors} connected")
        
        total_baseline = len(baseline)
        connected_baseline = sum(1 for r in baseline_results.values() if r.get('connected', False))
        print(f"  Baseline:  {connected_baseline}/{total_baseline} connected")
        
        # Overall status
        total_devices = total_motors + total_detectors + total_baseline
        connected_devices = connected_motors + connected_detectors + connected_baseline
        
        if connected_devices == total_devices:
            print(f"\n🎉 All devices connected successfully! ({connected_devices}/{total_devices})")
            return True
        else:
            print(f"\n⚠️  Some devices not connected ({connected_devices}/{total_devices})")
            return False
            
    except Exception as e:
        print(f"❌ Failed to load instrument: {e}")
        return False

def test_device_operations():
    """Test basic device operations."""
    print("\n" + "=" * 50)
    print("🔧 Device Operations Test")
    print("=" * 50)
    
    try:
        # Import bluesky plans
        exec("from my_beamline.startup import *", globals())
        RE = globals().get('RE')
        
        if not RE:
            print("❌ RunEngine not available")
            return False
            
        import bluesky.plans as bp
        import bluesky.plan_stubs as bps
        import bluesky.preprocessors as bpp
        
        # Test motor motion
        motors = list(bpp._devices_by_label.get('motors', []))
        if motors:
            test_motor = motors[0]  # Use first available motor
            print(f"🚗 Testing motor motion with {test_motor.name}:")
            
            try:
                initial_pos = test_motor.position
                print(f"  Initial position: {initial_pos:.3f}")
                
                # Small relative move
                move_amount = 0.1
                print(f"  Moving by +{move_amount}...")
                RE(bps.mvr(test_motor, move_amount))
                
                new_pos = test_motor.position
                print(f"  New position: {new_pos:.3f}")
                
                # Move back
                print(f"  Moving back by -{move_amount}...")
                RE(bps.mvr(test_motor, -move_amount))
                
                final_pos = test_motor.position
                print(f"  Final position: {final_pos:.3f}")
                print("  ✅ Motor motion test passed")
                
            except Exception as e:
                print(f"  ❌ Motor motion test failed: {e}")
        
        # Test detector counting
        detectors = list(bpp._devices_by_label.get('detectors', []))
        if detectors:
            test_detector = detectors[0]  # Use first available detector
            print(f"\n🔍 Testing detector counting with {test_detector.name}:")
            
            try:
                print("  Counting for 1 second...")
                RE(bp.count([test_detector], num=1))
                print("  ✅ Detector counting test passed")
                
            except Exception as e:
                print(f"  ❌ Detector counting test failed: {e}")
        
        print("\n✅ Device operations test completed")
        return True
        
    except Exception as e:
        print(f"❌ Device operations test failed: {e}")
        return False

def test_data_collection():
    """Test basic data collection."""
    print("\n" + "=" * 50)
    print("📊 Data Collection Test")  
    print("=" * 50)
    
    try:
        exec("from my_beamline.startup import *", globals())
        RE = globals().get('RE')
        cat = globals().get('cat')
        
        if not (RE and cat):
            print("❌ RunEngine or catalog not available")
            return False
            
        import bluesky.plans as bp
        import bluesky.preprocessors as bpp
        
        # Get devices
        motors = list(bpp._devices_by_label.get('motors', []))
        detectors = list(bpp._devices_by_label.get('detectors', []))
        
        if not (motors and detectors):
            print("❌ No motors or detectors available")
            return False
            
        test_motor = motors[0]
        test_detector = detectors[0]
        
        print(f"🔬 Testing scan: {test_motor.name} vs {test_detector.name}")
        
        # Record initial run count
        initial_runs = len(list(cat))
        
        # Perform a simple scan
        print("  Performing relative scan...")
        RE(bp.rel_scan([test_detector], test_motor, -0.2, 0.2, 5))
        
        # Check if run was saved
        final_runs = len(list(cat))
        new_runs = final_runs - initial_runs
        
        if new_runs > 0:
            print(f"  ✅ Scan completed, {new_runs} new run(s) in catalog")
            
            # Get the latest run
            latest_run = cat[-1]
            print(f"  Run metadata: {latest_run.metadata['start']['scan_id']}")
            print(f"  Data keys: {list(latest_run.primary.read().data_vars.keys())}")
            
            return True
        else:
            print("  ❌ No new runs found in catalog")
            return False
            
    except Exception as e:
        print(f"❌ Data collection test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 BITS Device Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Device Connectivity", test_device_connectivity),
        ("Device Operations", test_device_operations),
        ("Data Collection", test_data_collection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔄 Starting {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 50)
    print("📋 Final Test Results")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:<20}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your device configuration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())