#!/bin/bash

# Company License Maker
# Usage: ./company-license-maker.sh --start-date YYYY-MM-DD --end-date YYYY-MM-DD --output company-license.lic

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 --start-date YYYY-MM-DD --end-date YYYY-MM-DD --output company-license.lic"
    echo ""
    echo "Options:"
    echo "  --start-date    Start date in YYYY-MM-DD format"
    echo "  --end-date      End date in YYYY-MM-DD format"
    echo "  --output        Output filename (default: company-license.lic)"
    echo "  --help          Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --start-date 2025-01-01 --end-date 2025-12-31 --output client-license.lic"
}

# Parse command line arguments
START_DATE=""
END_DATE=""
OUTPUT_FILE="company-license.lic"

while [[ $# -gt 0 ]]; do
    case $1 in
        --start-date)
            START_DATE="$2"
            shift 2
            ;;
        --end-date)
            END_DATE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$START_DATE" || -z "$END_DATE" ]]; then
    print_error "Start date and end date are required"
    show_usage
    exit 1
fi

# Validate date format
if ! [[ "$START_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    print_error "Invalid start date format. Use YYYY-MM-DD"
    exit 1
fi

if ! [[ "$END_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    print_error "Invalid end date format. Use YYYY-MM-DD"
    exit 1
fi

# Validate that start date is before end date
START_TIMESTAMP=$(date -d "$START_DATE" +%s 2>/dev/null)
END_TIMESTAMP=$(date -d "$END_DATE" +%s 2>/dev/null)

if [[ $? -ne 0 ]]; then
    print_error "Invalid date format. Please use valid dates in YYYY-MM-DD format"
    exit 1
fi

if [[ $START_TIMESTAMP -ge $END_TIMESTAMP ]]; then
    print_error "Start date must be before end date"
    exit 1
fi

# Check if current date is within the license period
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIMESTAMP=$(date -d "$CURRENT_DATE" +%s)

if [[ $CURRENT_TIMESTAMP -lt $START_TIMESTAMP ]]; then
    print_warning "License start date is in the future"
elif [[ $CURRENT_TIMESTAMP -gt $END_TIMESTAMP ]]; then
    print_warning "License end date has already passed"
fi

# Generate license data as JSON first
LICENSE_JSON=$(cat <<EOF
{
  "startDate": "$START_DATE",
  "endDate": "$END_DATE",
  "issuedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "signature": "$(echo -n "$START_DATE$END_DATE" | openssl dgst -sha256 -hex | cut -d' ' -f2)"
}
EOF
)

# Encode to base64 and write to .lic file
echo "$LICENSE_JSON" | base64 -w 0 > "$OUTPUT_FILE"

print_status "Company license generated successfully!"
print_status "License file: $OUTPUT_FILE"
print_status "License period: $START_DATE to $END_DATE"
print_status ""
print_status "To apply this license:"
print_status "1. Copy $OUTPUT_FILE to the app directory"
print_status "2. Rename it to 'company-license.lic'"
print_status "3. Restart the application" 