#!/bin/bash
# Start Demo IOCs for BITS Tutorial
# This script starts both the adsim and gp IOCs for the tutorial

set -e  # Exit on any error

echo "🚀 Starting BITS Demo IOCs..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if podman is available
if ! command -v podman &> /dev/null; then
    echo -e "${RED}❌ Podman is not installed or not in PATH${NC}"
    echo "Please install Podman to run the demo IOCs"
    exit 1
fi

# Function to check if container is running
check_container() {
    local container_name=$1
    if podman ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        return 0  # Container is running
    else
        return 1  # Container is not running
    fi
}

# Function to stop and remove existing container
cleanup_container() {
    local container_name=$1
    echo "🧹 Cleaning up existing ${container_name} container..."
    
    if check_container "${container_name}"; then
        podman stop "${container_name}" >/dev/null 2>&1
    fi
    
    if podman ps -a --format "{{.Names}}" | grep -q "^${container_name}$"; then
        podman rm "${container_name}" >/dev/null 2>&1
    fi
}

# Function to start IOC container
start_ioc() {
    local container_name=$1
    local ioc_type=$2
    local prefix=$3
    
    echo "🔧 Starting ${container_name} (${ioc_type} IOC with prefix '${prefix}')..."
    
    # Start container in detached mode
    if podman run -d -it --rm \
        --name "${container_name}" \
        --net=host \
        -e "PREFIX=${prefix}" \
        epics-podman:latest "${ioc_type}" >/dev/null 2>&1; then
        
        echo -e "${GREEN}✅ ${container_name} started successfully${NC}"
        
        # Wait a moment for IOC to initialize
        sleep 3
        
        # Test connectivity
        echo "   Testing PV connectivity..."
        if timeout 10 python3 -c "
import time
try:
    import epics
    test_pv = f'${prefix}IOC_CPU_LOAD' if ioc_type == 'gp' else f'${prefix}cam1:Acquire'
    pv = epics.PV(test_pv)
    if pv.wait_for_connection(timeout=5):
        print(f'   📡 Connected to {test_pv}')
        exit(0)
    else:
        exit(1)
except ImportError:
    print('   ⚠️  PyEPICS not available - cannot test connectivity')
    exit(0)
except Exception as e:
    print(f'   ❌ Connection test failed: {e}')
    exit(1)
" 2>/dev/null; then
            echo -e "${GREEN}   ✅ IOC is responding to EPICS requests${NC}"
        else
            echo -e "${YELLOW}   ⚠️  Cannot verify EPICS connectivity (IOC may still be starting)${NC}"
        fi
        
    else
        echo -e "${RED}❌ Failed to start ${container_name}${NC}"
        return 1
    fi
}

# Check if epics-podman image is available
echo "🔍 Checking for epics-podman container image..."
if ! podman images | grep -q epics-podman; then
    echo -e "${YELLOW}⚠️  epics-podman image not found locally${NC}"
    echo "Pulling from registry (this may take a few minutes)..."
    if podman pull ghcr.io/bcda-aps/bits/epics-container:latest; then
        # Tag the image for local use
        podman tag ghcr.io/bcda-aps/bits/epics-container:latest epics-podman:latest
        echo -e "${GREEN}✅ Container image downloaded and tagged${NC}"
    else
        echo -e "${RED}❌ Failed to pull container image${NC}"
        echo "Please check your internet connection and try again"
        exit 1
    fi
else
    echo -e "${GREEN}✅ epics-podman image found${NC}"
fi

# Clean up any existing containers
cleanup_container "adsim_ioc"
cleanup_container "gp_ioc"

# Start Area Detector IOC
echo ""
echo "1️⃣  Area Detector IOC"
start_ioc "adsim_ioc" "adsim" "adsim:"

# Start General Purpose IOC  
echo ""
echo "2️⃣  General Purpose IOC"
start_ioc "gp_ioc" "gp" "gp:"

echo ""
echo -e "${GREEN}🎉 Demo IOCs started successfully!${NC}"
echo ""
echo "📊 IOC Summary:"
echo "   adsim_ioc: Area detector simulation (prefix: adsim:)"
echo "   gp_ioc:    General purpose devices (prefix: gp:)"
echo ""
echo "🔧 Useful Commands:"
echo "   podman ps                    # Check container status"
echo "   podman logs adsim_ioc        # View adsim IOC logs"
echo "   podman logs gp_ioc           # View gp IOC logs"
echo "   podman exec -it gp_ioc bash  # Connect to gp IOC shell"
echo ""
echo "🔍 Test Connectivity:"
echo "   python scripts/explore_iocs.py --test-connectivity"
echo ""
echo "🛑 To Stop IOCs:"
echo "   ./scripts/stop_demo_iocs.sh"
echo ""

# Check final status
echo "📋 Final Status Check:"
if check_container "adsim_ioc" && check_container "gp_ioc"; then
    echo -e "${GREEN}✅ Both IOCs are running${NC}"
    echo ""
    echo "🚀 Ready for tutorial! Next step:"
    echo "   python scripts/explore_iocs.py"
    exit 0
else
    echo -e "${RED}❌ One or more IOCs failed to start properly${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check container logs: podman logs adsim_ioc"
    echo "   2. Check if ports are in use: netstat -ln | grep 5064"
    echo "   3. Try stopping and restarting: ./scripts/stop_demo_iocs.sh && ./scripts/start_demo_iocs.sh"
    exit 1
fi
