#!/bin/bash
# Stop Demo IOCs for BITS Tutorial

echo "🛑 Stopping BITS Demo IOCs..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to stop and remove container
stop_container() {
    local container_name=$1
    
    if podman ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        echo "🛑 Stopping ${container_name}..."
        podman stop "${container_name}" >/dev/null 2>&1
        echo -e "${GREEN}✅ ${container_name} stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  ${container_name} is not running${NC}"
    fi
    
    if podman ps -a --format "{{.Names}}" | grep -q "^${container_name}$"; then
        echo "🗑️  Removing ${container_name} container..."
        podman rm "${container_name}" >/dev/null 2>&1
        echo -e "${GREEN}✅ ${container_name} removed${NC}"
    fi
}

# Stop both IOCs
stop_container "adsim_ioc"
stop_container "gp_ioc"

echo ""
echo -e "${GREEN}🎉 Demo IOCs stopped successfully!${NC}"
echo ""
echo "To restart IOCs: ./scripts/start_demo_iocs.sh"