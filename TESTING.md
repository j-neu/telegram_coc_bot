# Testing Guide

## Strategy 1: Private Test Group (Start Here)

1. Create a new private Telegram group ("CoC Bot Test")
2. Add 2–3 test accounts (friends or secondary accounts)
3. Add the bot as admin with "Delete messages" and "Restrict members" permissions
4. Set `DRY_RUN=false` — test with real enforcement

Test scenarios to run:
- Have a test account send a message before agreeing → verify message is deleted and user is restricted
- Verify the bot sends a DM to the test account with an Agree button
- Tap Agree → verify user is unrestricted and can now post
- Have another test account block DMs from unknown bots → verify bot falls back to inline group message
- Have the same account join a second test group → verify the cross-group fast-path (confirm-only, not full CoC)
- Run `/setversion 2.0` → verify all users must re-agree

## Strategy 2: Dry-Run in Production

Set `DRY_RUN=true` before adding the bot to a production group:
- Bot logs what it would do without restricting anyone or deleting messages
- Agreements are still recorded to the database
- Use this to verify the bot is detecting messages correctly before going live

Switch to `DRY_RUN=false` when ready to enforce.

## Testing Checklist

- [ ] Message from non-agreed user is deleted within ~2 seconds
- [ ] User is restricted after message deletion
- [ ] DM with Agree button is sent to restricted user
- [ ] Inline group fallback fires when user has DMs blocked
- [ ] Tapping Agree unrestricts the user
- [ ] Agreement is recorded in PostgreSQL
- [ ] Cross-group fast-path shown for users already agreed elsewhere
- [ ] Fast-path confirm records agreement for the new group
- [ ] New member join triggers immediate restriction + DM
- [ ] `/whoagreed` returns correct list for this group
- [ ] `/setversion` forces re-agreement for all users
- [ ] Admin commands reject non-admin users
- [ ] Database data persists across a Railway redeploy (redeploy and verify existing agreements still present)

## Common Issues

### Bot doesn't delete messages
- Check bot has "Delete messages" admin permission in the group
- Verify bot is actually an admin (not just a member)

### Bot can't restrict users
- Check "Restrict members" admin permission is enabled
- Group must not be a channel

### DM not received
- Expected if user has blocked DMs from unknown bots — the inline fallback should fire instead
- If neither fires, check logs for errors

### Cross-group fast-path not appearing
- Verify `has_agreed_anywhere()` is querying across all `group_id` values for that `user_id`
- Check the `coc_version` matches exactly (string comparison)

### Data lost after Railway redeploy
- This means the bot is writing to the local filesystem, not PostgreSQL
- Verify `DATABASE_URL` env var is set and the bot is connecting to it, not creating a local SQLite file
