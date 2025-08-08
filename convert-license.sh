#!/bin/bash

# License Converter Script
# Converts JSON license files to base64 encoded .lic files

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
    echo "Usage: $0 --input input.json --output output.lic"
    echo ""
    echo "Options:"
    echo "  --input     Input JSON license file"
    echo "  --output    Output .lic file"
    echo "  --help      Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --input license.json --output license.lic"
    echo "  $0 --input company-license.json --output company-license.lic"
}

# Parse command line arguments
INPUT_FILE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_FILE="$2"
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
if [[ -z "$INPUT_FILE" || -z "$OUTPUT_FILE" ]]; then
    print_error "Input and output files are required"
    show_usage
    exit 1
fi

# Check if input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    print_error "Input file '$INPUT_FILE' does not exist"
    exit 1
fi

# Validate JSON format
if ! jq empty "$INPUT_FILE" 2>/dev/null; then
    print_error "Input file '$INPUT_FILE' is not valid JSON"
    exit 1
fi

# Convert JSON to base64 encoded .lic file
print_status "Converting $INPUT_FILE to $OUTPUT_FILE..."

# Read JSON and encode to base64
cat "$INPUT_FILE" | base64 -w 0 > "$OUTPUT_FILE"

if [[ $? -eq 0 ]]; then
    print_status "Successfully converted $INPUT_FILE to $OUTPUT_FILE"
    print_status "Original file size: $(wc -c < "$INPUT_FILE") bytes"
    print_status "Encoded file size: $(wc -c < "$OUTPUT_FILE") bytes"
else
    print_error "Failed to convert file"
    exit 1
fi

print_status ""
print_status "To apply the new license:"
print_status "1. Backup your original $INPUT_FILE"
print_status "2. Replace $INPUT_FILE with $OUTPUT_FILE"
print_status "3. Restart the application" 