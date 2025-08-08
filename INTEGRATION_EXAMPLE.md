# Integration Example

Here's how to integrate the combined license system into your main application:

## 1. Import the Combined License Module

In your main `app.module.ts`:

```typescript
import { Module } from '@nestjs/common';
import { CombinedLicenseModule } from './core/combined-license/combined-license.module';

@Module({
  imports: [
    // ... your other modules
    CombinedLicenseModule,
  ],
  // ... rest of your module config
})
export class AppModule {}
```

## 2. Use the Combined Global Guard

In your main `main.ts`:

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { CombinedLicenseGlobalGuard } from './core/combined-license/combined-license-global.guard';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Apply the combined license guard globally
  const combinedLicenseGuard = app.get(CombinedLicenseGlobalGuard);
  app.useGlobalGuards(combinedLicenseGuard);

  await app.listen(3000);
}
bootstrap();
```

## 3. Use in Controllers for Module Access

In your controllers:

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import { CombinedLicenseValidator } from './core/combined-license/combined-license.validator';

@Controller('auth')
export class AuthController {
  constructor(
    private readonly combinedLicenseValidator: CombinedLicenseValidator,
  ) {}

  @Get('status')
  getAuthStatus() {
    // Check if auth module is accessible
    const canAccessAuth = this.combinedLicenseValidator.validateModule('auth');

    if (!canAccessAuth) {
      throw new ForbiddenException('Auth module access denied');
    }

    return { status: 'Auth module is accessible' };
  }
}
```

## 4. Monitor License Status

Create a license status endpoint:

```typescript
import { Controller, Get } from '@nestjs/common';
import { CombinedLicenseValidator } from './core/combined-license/combined-license.validator';
import { CombinedLicenseGuardService } from './core/combined-license/combined-license.guard.service';

@Controller('license')
export class LicenseController {
  constructor(
    private readonly combinedLicenseValidator: CombinedLicenseValidator,
    private readonly combinedLicenseGuardService: CombinedLicenseGuardService,
  ) {}

  @Get('status')
  getLicenseStatus() {
    return {
      validation: this.combinedLicenseValidator.getValidationStatus(),
      lockStatus: this.combinedLicenseGuardService.getLockStatus(),
      isLocked: this.combinedLicenseGuardService.isApplicationLocked(),
    };
  }

  @Get('check')
  forceCheckLicenses() {
    const isValid = this.combinedLicenseGuardService.forceCheckLicenses();
    return { valid: isValid };
  }
}
```

## 5. Environment Variables (Optional)

You can add environment variables to control license checking intervals:

```typescript
// In your .env file
LICENSE_CHECK_INTERVAL=300000  # 5 minutes in milliseconds
LICENSE_ENABLED=true

// In your combined license guard service
@Interval(process.env.LICENSE_CHECK_INTERVAL || 5 * 60 * 1000)
private checkCombinedLicense() {
  if (process.env.LICENSE_ENABLED === 'false') {
    return; // Skip license checking
  }
  // ... rest of the check logic
}
```

## 6. Error Handling

The system automatically handles license errors:

- **423 Locked**: When either license is invalid
- **Detailed error messages**: Indicating which license failed
- **Automatic file cleanup**: Invalid license files are removed

## 7. Testing

To test the system:

1. **Valid both licenses**: Application works normally
2. **Invalid developer license**: Application locks with `LGPS2_LICENSE_INVALID`
3. **Invalid company license**: Application locks with `COMPANY_LICENSE_INVALID`
4. **Invalid both licenses**: Application locks with `BOTH_LICENSES_INVALID`

## 8. Production Deployment

For production:

1. **Generate company license** using the script
2. **Place both license files** in the app directory:
   - `license.json` (your developer license)
   - `company-license.json` (company license)
3. **Restart the application**
4. **Monitor license status** using the `/license/status` endpoint

## 9. Security Considerations

- **File permissions**: Ensure license files are readable by the application
- **Backup**: Keep copies of valid licenses
- **Monitoring**: Set up alerts for license expiration
- **Grace period**: Consider implementing a grace period for license renewal

## 10. Troubleshooting Integration

If the integration doesn't work:

1. **Check module imports**: Ensure `CombinedLicenseModule` is imported
2. **Verify guard registration**: Ensure the global guard is applied
3. **Check file paths**: Ensure license files are in the correct location
4. **Review logs**: Check application logs for license validation errors
