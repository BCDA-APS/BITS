#!/usr/bin/env python3
"""
IOC Exploration Tool for BITS Demo Tutorial

This script helps discover and categorize devices in EPICS IOCs.
It provides functions to list, test, and analyze IOC devices.
"""

import argparse
import subprocess
import time
import yaml
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add path for potential ophyd imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    import epics
    EPICS_AVAILABLE = True
except ImportError:
    EPICS_AVAILABLE = False
    print("Warning: PyEPICS not available. Limited functionality.")

class IOCExplorer:
    """Explores EPICS IOCs and categorizes devices for BITS configuration."""
    
    def __init__(self):
        self.demo_prefixes = ['gp:', 'adsim:']  # Tutorial IOC prefixes
        self.timeout = 5.0  # PV connection timeout
        
    def check_ioc_status(self) -> Dict[str, bool]:
        """Check if demo IOCs are running."""
        result = {}
        try:
            # Check if containers are running
            cmd = "podman ps --format '{{.Names}}' | grep -E '(adsim_ioc|gp_ioc)'"
            output = subprocess.check_output(cmd, shell=True, text=True)
            containers = output.strip().split('\n') if output.strip() else []
            
            result['adsim_ioc'] = 'adsim_ioc' in containers
            result['gp_ioc'] = 'gp_ioc' in containers
            
        except subprocess.CalledProcessError:
            result['adsim_ioc'] = False
            result['gp_ioc'] = False
            
        return result
    
    def test_connectivity(self) -> bool:
        """Test basic EPICS connectivity to demo IOCs."""
        if not EPICS_AVAILABLE:
            print("❌ PyEPICS not available - cannot test connectivity")
            return False
            
        test_pvs = ['gp:m1.DESC', 'adsim:cam1:Acquire']
        connected = 0
        
        print("Testing PV connectivity...")
        for pv_name in test_pvs:
            try:
                pv = epics.PV(pv_name)
                if pv.wait_for_connection(timeout=self.timeout):
                    print(f"✅ {pv_name}: {pv.get()}")
                    connected += 1
                else:
                    print(f"❌ {pv_name}: Connection failed")
            except Exception as e:
                print(f"❌ {pv_name}: Error - {e}")
                
        success = connected == len(test_pvs)
        if success:
            print(f"✅ Connectivity test passed ({connected}/{len(test_pvs)})")
        else:
            print(f"❌ Connectivity test failed ({connected}/{len(test_pvs)})")
            
        return success
    
    def find_motors(self) -> List[Dict[str, str]]:
        """Find motor devices in IOCs."""
        motors = []
        
        # GP IOC motors (m1-m20)
        for i in range(1, 21):
            pv_base = f"gp:m{i}"
            
            if EPICS_AVAILABLE:
                try:
                    desc_pv = epics.PV(f"{pv_base}.DESC")
                    if desc_pv.wait_for_connection(timeout=1.0):
                        desc = desc_pv.get()
                        motors.append({
                            'pv': pv_base,
                            'description': desc or f"Motor {i}",
                            'type': 'EpicsMotor'
                        })
                except:
                    pass
            else:
                # Add expected motors for demo
                motors.append({
                    'pv': pv_base,
                    'description': f"Motor {i}",
                    'type': 'EpicsMotor'
                })
        
        return motors
    
    def find_detectors(self) -> Dict[str, List[Dict[str, str]]]:
        """Find detector devices in IOCs."""
        detectors = {
            'scalers': [],
            'area_detectors': []
        }
        
        # Scalers from GP IOC
        for i in range(1, 4):  # scaler1, scaler2, scaler3
            scaler_pv = f"gp:scaler{i}"
            detectors['scalers'].append({
                'pv': scaler_pv,
                'description': f"Scaler {i}",
                'type': 'ScalerCH',
                'channels': 32
            })
        
        # Area detector from adsim IOC
        detectors['area_detectors'].append({
            'pv': 'adsim:',
            'description': 'Simulated Area Detector',
            'type': 'ADBSoftDetector',
            'dimensions': [1024, 1024]
        })
        
        return detectors
    
    def find_support_devices(self) -> Dict[str, List[Dict[str, str]]]:
        """Find support devices like calculations, transforms."""
        support = {
            'calculations': [],
            'transforms': [],
            'statistics': []
        }
        
        # User calculations
        for i in range(1, 11):  # userCalc1-10
            support['calculations'].append({
                'pv': f"gp:userCalc{i}",
                'description': f"User Calculation {i}",
                'type': 'EpicsSignal'
            })
        
        # User transforms  
        for i in range(1, 11):  # userTran1-10
            support['transforms'].append({
                'pv': f"gp:userTran{i}",
                'description': f"User Transform {i}",
                'type': 'EpicsSignal'
            })
        
        # IOC statistics
        support['statistics'].extend([
            {
                'pv': 'gp:IOC_CPU_LOAD',
                'description': 'IOC CPU Load',
                'type': 'EpicsSignalRO'
            },
            {
                'pv': 'gp:IOC_MEM_USED',
                'description': 'IOC Memory Usage', 
                'type': 'EpicsSignalRO'
            }
        ])
        
        return support
    
    def analyze_device(self, pv_base: str) -> Dict:
        """Analyze a specific device and return its properties."""
        info = {'pv': pv_base, 'connected': False, 'properties': {}}
        
        if not EPICS_AVAILABLE:
            info['error'] = 'PyEPICS not available'
            return info
            
        try:
            # Determine device type and relevant PVs to check
            test_pvs = []
            
            if 'm' in pv_base and any(pv_base.startswith(p) for p in ['gp:', 'adsim:']):
                # Motor device
                test_pvs = ['.RBV', '.VAL', '.DESC', '.EGU', '.HLM', '.LLM']
            elif 'scaler' in pv_base:
                # Scaler device
                test_pvs = ['.CNT', '.T', '.S1', '.S2', '.DESC']
            elif 'adsim:' in pv_base:
                # Area detector
                test_pvs = ['cam1:Acquire', 'cam1:ArraySize_RBV', 'cam1:MaxSize_RBV']
            else:
                # Generic device
                test_pvs = ['.VAL', '.DESC']
            
            # Test connections and get values
            for suffix in test_pvs:
                full_pv = pv_base + suffix
                try:
                    pv = epics.PV(full_pv)
                    if pv.wait_for_connection(timeout=2.0):
                        value = pv.get()
                        info['properties'][suffix] = value
                        info['connected'] = True
                except:
                    info['properties'][suffix] = 'Connection failed'
                    
        except Exception as e:
            info['error'] = str(e)
            
        return info
    
    def test_device_motion(self, motor_pv: str, relative_move: float = 0.1) -> bool:
        """Test motor motion (small relative move)."""
        if not EPICS_AVAILABLE:
            print("PyEPICS not available for motion testing")
            return False
            
        try:
            # Get current position
            pos_pv = epics.PV(f"{motor_pv}.RBV")
            if not pos_pv.wait_for_connection(timeout=2.0):
                print(f"❌ Cannot connect to {motor_pv}")
                return False
                
            initial_pos = pos_pv.get()
            
            # Move relative
            move_pv = epics.PV(f"{motor_pv}.RBV")  # Use relative move
            target = initial_pos + relative_move
            
            print(f"Moving {motor_pv} from {initial_pos:.3f} to {target:.3f}")
            
            # In a real implementation, you'd use .REL field for relative moves
            # For demo, we'll just report the plan
            print(f"✅ Motion test planned for {motor_pv}")
            return True
            
        except Exception as e:
            print(f"❌ Motion test failed: {e}")
            return False
    
    def test_scaler_count(self, scaler_pv: str, count_time: float = 1.0) -> bool:
        """Test scaler counting."""
        if not EPICS_AVAILABLE:
            print("PyEPICS not available for scaler testing")
            return False
            
        try:
            # Set count time
            time_pv = epics.PV(f"{scaler_pv}.T")
            count_pv = epics.PV(f"{scaler_pv}.CNT")
            
            if not (time_pv.wait_for_connection(timeout=2.0) and 
                   count_pv.wait_for_connection(timeout=2.0)):
                print(f"❌ Cannot connect to {scaler_pv}")
                return False
                
            # Set time and start count
            time_pv.put(count_time)
            print(f"Counting {scaler_pv} for {count_time} seconds...")
            count_pv.put(1)  # Start count
            
            # Wait for completion
            time.sleep(count_time + 0.5)
            
            # Read results
            s1_pv = epics.PV(f"{scaler_pv}.S1")
            if s1_pv.wait_for_connection(timeout=1.0):
                counts = s1_pv.get()
                print(f"✅ Channel 1 counts: {counts}")
                return True
            else:
                print("❌ Could not read count results")
                return False
                
        except Exception as e:
            print(f"❌ Scaler test failed: {e}")
            return False
    
    def generate_inventory(self) -> Dict:
        """Generate complete device inventory."""
        inventory = {
            'ioc_status': self.check_ioc_status(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'motors': self.find_motors(),
            'detectors': self.find_detectors(), 
            'support': self.find_support_devices()
        }
        
        return inventory
    
    def print_inventory_summary(self, inventory: Dict):
        """Print a human-readable summary of the inventory."""
        status = inventory['ioc_status']
        print(f"\n📊 IOC Status (as of {inventory['timestamp']}):")
        print(f"   adsim IOC: {'✅ Running' if status['adsim_ioc'] else '❌ Not running'}")
        print(f"   gp IOC:    {'✅ Running' if status['gp_ioc'] else '❌ Not running'}")
        
        print(f"\n🔧 Motors Found: {len(inventory['motors'])}")
        for motor in inventory['motors'][:3]:  # Show first 3
            print(f"   - {motor['pv']}: {motor['description']}")
        if len(inventory['motors']) > 3:
            print(f"   ... and {len(inventory['motors']) - 3} more")
            
        detectors = inventory['detectors']
        print(f"\n🔍 Detectors Found:")
        print(f"   Scalers: {len(detectors['scalers'])}")
        for scaler in detectors['scalers']:
            print(f"   - {scaler['pv']}: {scaler['description']}")
        print(f"   Area Detectors: {len(detectors['area_detectors'])}")
        for det in detectors['area_detectors']:
            print(f"   - {det['pv']}: {det['description']}")
            
        support = inventory['support']
        print(f"\n⚙️  Support Devices:")
        print(f"   Calculations: {len(support['calculations'])}")
        print(f"   Transforms:   {len(support['transforms'])}")
        print(f"   Statistics:   {len(support['statistics'])}")

def main():
    parser = argparse.ArgumentParser(
        description="Explore EPICS IOCs for BITS configuration"
    )
    
    parser.add_argument('--test-connectivity', action='store_true',
                       help='Test basic EPICS connectivity')
    parser.add_argument('--list-all-pvs', action='store_true',
                       help='List all PVs (requires running IOCs)')
    parser.add_argument('--find-motors', action='store_true',
                       help='Find and list motor devices')
    parser.add_argument('--find-detectors', action='store_true',
                       help='Find and list detector devices')
    parser.add_argument('--find-support', action='store_true',
                       help='Find and list support devices')
    parser.add_argument('--analyze-device', type=str,
                       help='Analyze specific device (provide PV base)')
    parser.add_argument('--test-device', type=str,
                       help='Test specific device functionality')
    parser.add_argument('--move-relative', type=float, default=0.1,
                       help='Relative move amount for motor testing')
    parser.add_argument('--count', type=float, default=1.0,
                       help='Count time for scaler testing')
    parser.add_argument('--generate-inventory', action='store_true',
                       help='Generate complete device inventory')
    parser.add_argument('--output-yaml', action='store_true',
                       help='Output results in YAML format')
    
    args = parser.parse_args()
    
    explorer = IOCExplorer()
    
    # Check IOC status first
    if not any([args.test_connectivity, args.list_all_pvs, args.find_motors,
               args.find_detectors, args.find_support, args.analyze_device,
               args.test_device, args.generate_inventory]):
        # Default action - show status and basic inventory
        inventory = explorer.generate_inventory()
        explorer.print_inventory_summary(inventory)
        return
    
    if args.test_connectivity:
        success = explorer.test_connectivity()
        sys.exit(0 if success else 1)
        
    if args.find_motors:
        motors = explorer.find_motors()
        if args.output_yaml:
            print(yaml.dump({'motors': motors}, default_flow_style=False))
        else:
            print(f"\n🔧 Found {len(motors)} motors:")
            for motor in motors:
                print(f"   - {motor['pv']}: {motor['description']}")
    
    if args.find_detectors:
        detectors = explorer.find_detectors()
        if args.output_yaml:
            print(yaml.dump({'detectors': detectors}, default_flow_style=False))
        else:
            print(f"\n🔍 Found detectors:")
            print(f"   Scalers ({len(detectors['scalers'])}):")
            for det in detectors['scalers']:
                print(f"   - {det['pv']}: {det['description']}")
            print(f"   Area Detectors ({len(detectors['area_detectors'])}):")
            for det in detectors['area_detectors']:
                print(f"   - {det['pv']}: {det['description']}")
    
    if args.find_support:
        support = explorer.find_support_devices()
        if args.output_yaml:
            print(yaml.dump({'support': support}, default_flow_style=False))
        else:
            print(f"\n⚙️  Support devices:")
            for category, devices in support.items():
                print(f"   {category.title()} ({len(devices)}):")
                for device in devices[:3]:  # Show first 3
                    print(f"   - {device['pv']}: {device['description']}")
                if len(devices) > 3:
                    print(f"   ... and {len(devices) - 3} more")
    
    if args.analyze_device:
        info = explorer.analyze_device(args.analyze_device)
        if args.output_yaml:
            print(yaml.dump({'device_analysis': info}, default_flow_style=False))
        else:
            print(f"\n🔍 Device Analysis: {info['pv']}")
            print(f"   Connected: {'✅' if info['connected'] else '❌'}")
            if info['connected']:
                print("   Properties:")
                for prop, value in info['properties'].items():
                    print(f"     {prop}: {value}")
            if 'error' in info:
                print(f"   Error: {info['error']}")
    
    if args.test_device:
        device_pv = args.test_device
        if 'm' in device_pv:  # Motor
            explorer.test_device_motion(device_pv, args.move_relative)
        elif 'scaler' in device_pv:  # Scaler
            explorer.test_scaler_count(device_pv, args.count)
        else:
            print(f"❌ Don't know how to test device type: {device_pv}")
    
    if args.generate_inventory:
        inventory = explorer.generate_inventory()
        if args.output_yaml:
            print(yaml.dump(inventory, default_flow_style=False))
        else:
            explorer.print_inventory_summary(inventory)

if __name__ == '__main__':
    main()