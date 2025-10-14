# Testing Guide

## Safe Testing Strategies

### Strategy 1: Private Test Group (RECOMMENDED)

1. **Create a test group**:
   - Create a new private Telegram group
   - Name it "CoC Bot Test" or similar
   - Add 2-3 alternative accounts (ask friends or use test accounts)

2. **Add the bot**:
   - Add your bot to the test group
   - Make it an admin with "Restrict members" permission

3. **Test scenarios**:
   - Have a test account join the group
   - Verify they get restricted and receive the CoC message
   - Click "Agree" and verify they get unrestricted
   - Test all admin commands
   - Check Google Sheets to verify data is recorded

4. **Verify in Google Sheets**:
   - Check that test data appears correctly
   - You can delete test rows manually before production use

### Strategy 2: Dry-Run Mode (Added Below)

Use the new `DRY_RUN` mode that logs actions without actually restricting users or modifying permissions.

### Strategy 3: Staged Rollout

1. **Phase 1: Monitoring Only**
   - Add bot to production group but keep `DRY_RUN=true`
   - Monitor logs to see what would happen
   - Verify Google Sheets integration works

2. **Phase 2: Admin Testing**
   - Test admin commands in production group
   - Use `/sendcode` to send a voluntary agreement request
   - Check who agrees without restrictions

3. **Phase 3: New Members Only**
   - Set `DRY_RUN=false`
   - Only new members will be restricted
   - Existing members are unaffected unless you run `/sendcode`

4. **Phase 4: Full Deployment**
   - Once confident, use `/sendcode` to prompt existing members

## Testing Checklist

- [ ] Bot can connect to Google Sheets
- [ ] Bot receives messages in test group
- [ ] New member gets restricted (or logged in dry-run mode)
- [ ] New member receives CoC message (DM or group)
- [ ] Clicking "Agree" records data to Google Sheets
- [ ] Clicking "Agree" unrestricts user (or logs in dry-run mode)
- [ ] `/whoagreed` shows correct users
- [ ] `/sendcode` sends CoC message to group
- [ ] Admin commands only work for configured admin IDs
- [ ] Non-admin users cannot use admin commands

## Common Test Issues

### Bot doesn't restrict users
- Check bot has "Restrict members" permission
- Verify bot is actually an admin
- Check logs for error messages

### Can't send DM to test users
- Test users must `/start` the bot first to enable DMs
- Otherwise bot will fallback to group message (expected behavior)

### Google Sheets errors
- Verify service account has Editor access to sheet
- Check `credentials.json` is in correct location
- Confirm SHEET_ID is correct

## Cleaning Up Test Data

After testing, you can:
1. Delete test rows from Google Sheet manually
2. Create a new sheet for production
3. Keep test data - it won't affect production operations
