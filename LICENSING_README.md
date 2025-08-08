# Dual License System

This application uses a dual-license system where both licenses must be valid for the application to work (AND gate logic).

## License Types

### 1. Developer License (lgps2)

- **Purpose**: Your license as the developer
- **File**: `license.lic` (base64 encoded)
- **Validation**: Uses public key cryptography
- **Features**: Module-based access control, customer ID tracking

### 2. Company License

- **Purpose**: License for the company selling the app to customers
- **File**: `company-license.lic` (base64 encoded)
- **Validation**: Simple date-based validation with signature
- **Features**: Start/end date control

## How It Works

The application will only work when **BOTH** licenses are valid:

- ✅ Developer License Valid + Company License Valid = Application Works
- ❌ Developer License Invalid + Company License Valid = Application Locked
- ❌ Developer License Valid + Company License Invalid = Application Locked
- ❌ Developer License Invalid + Company License Invalid = Application Locked

## Company License Maker

### Usage

```bash
./company-license-maker.sh --start-date YYYY-MM-DD --end-date YYYY-MM-DD --output company-license.lic
```

### Examples

```bash
# Create a license for 2025
./company-license-maker.sh --start-date 2025-01-01 --end-date 2025-12-31 --output client-license.lic

# Create a short-term license
./company-license-maker.sh --start-date 2025-01-01 --end-date 2025-01-31 --output trial-license.lic

# Create a license with custom output name
./company-license-maker.sh --start-date 2025-01-01 --end-date 2025-06-30 --output my-client-license.lic
```

### Output

The script generates a base64 encoded `company-license.lic` file containing:

```json
{
  "startDate": "2025-01-01",
  "endDate": "2025-12-31",
  "issuedAt": "2025-01-15T10:30:00Z",
  "signature": "abc123..."
}
```

## Converting Existing Licenses

If you have existing JSON license files, convert them to `.lic` format:

```bash
# Convert your developer license
./convert-license.sh --input license.json --output license.lic

# Convert company license
./convert-license.sh --input company-license.json --output company-license.lic
```

## Installation

### For the Company (selling the app)

1. **Generate License**:

   ```bash
   ./company-license-maker.sh --start-date 2025-01-01 --end-date 2025-12-31 --output client-license.lic
   ```

2. **Apply License**:
   - Copy the generated file to the app directory
   - Rename it to `company-license.lic`
   - Restart the application

### For the Developer (you)

1. **Convert your existing license**:

   ```bash
   ./convert-license.sh --input license.json --output license.lic
   ```

2. **Both licenses** must be valid for the app to work

## Application Integration

The application automatically:

1. **Checks both licenses** every 5 minutes
2. **Locks the application** if either license is invalid
3. **Provides generic error messages** (no license system details exposed)
4. **Validates module access** based on both licenses

## Error Handling

When the application is locked, you'll receive a generic error:

```json
{
  "error": "Application Locked",
  "message": "Service temporarily unavailable",
  "code": "SERVICE_UNAVAILABLE"
}
```

**No license system details are exposed to clients!**

## Security Features

1. **Base64 encoded files**: License files are not human-readable
2. **Automatic file removal**: Invalid license files are automatically deleted
3. **Signature validation**: Both licenses use cryptographic signatures
4. **Regular checks**: Licenses are validated every 5 minutes
5. **Graceful degradation**: Application locks immediately when licenses become invalid
6. **Generic error messages**: No internal system details exposed

## Troubleshooting

### Application won't start

1. Check if `license.lic` exists and is valid
2. Check if `company-license.lic` exists and is valid
3. Verify both license dates are within the current time range

### Application locks after running

1. Check license expiration dates
2. Verify license signatures
3. Ensure both license files are present and readable

### Module access denied

1. Check if the module is included in your lgps2 license
2. Verify company license is still valid
3. Both conditions must be met for module access

## File Structure

```
geo-backend/
├── license.lic              # Your developer license (base64 encoded)
├── company-license.lic      # Company license (base64 encoded)
├── company-license-maker.sh # License generation script
├── convert-license.sh       # License converter script
└── src/core/
    ├── lgps2/               # Developer license system
    ├── company-license/      # Company license system
    └── combined-license/     # Combined validation system
```

## Migration from JSON to .lic

If you're upgrading from JSON format:

1. **Convert your developer license**:

   ```bash
   ./convert-license.sh --input license.json --output license.lic
   ```

2. **Convert company license** (if exists):

   ```bash
   ./convert-license.sh --input company-license.json --output company-license.lic
   ```

3. **Remove old JSON files**:

   ```bash
   rm license.json company-license.json
   ```

4. **Restart the application**
