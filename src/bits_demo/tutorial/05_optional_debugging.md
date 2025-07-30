## Validation and Testing

### 1. Test Device Responsiveness
```bash
# Test motor motion
python scripts/explore_iocs.py --test-device gp:m1 --move-relative 0.1

# Test scaler counting
python scripts/explore_iocs.py --test-device gp:scaler1 --count 1.0

# Test area detector
python scripts/explore_iocs.py --test-device adsim: --acquire 1
```

### 2. Check Data Rates
```bash
# Monitor update rates
python scripts/explore_iocs.py --monitor-rates gp:m1.RBV gp:scaler1.S1

# Typical rates:
# - Motors: ~10 Hz position updates
# - Scalers: Variable (depends on counting)
# - Area detectors: Frame-rate dependent
```

### 3. Identify Connection Issues
```bash
# Check for disconnected PVs
python scripts/explore_iocs.py --check-connections

# Any PVs that don't connect may indicate:
# - IOC not running
# - Network issues  
# - Incorrect PV names
```
