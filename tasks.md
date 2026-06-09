# Developer Task Breakdown

## 1. Setup & Configuration

- [x] Create bot via [@BotFather](https://t.me/BotFather), get token
- [x] Create Railway project, add PostgreSQL plugin
- [x] Configure environment variables (WEBHOOK_URL set after first deploy):
  ```
  BOT_TOKEN=<telegram-bot-token>
  ADMIN_IDS=<comma-separated-admin-user-ids>
  COC_VERSION=1.0
  COC_LINK=https://your-code-of-conduct-url
  DATABASE_URL=<railway-postgres-url>
  WEBHOOK_URL=<railway-public-url>
  DRY_RUN=false
  ```

---

## 2. Database (PostgreSQL)

- [x] Connect via `psycopg2` using `DATABASE_URL`
- [x] Create `agreements` table on startup:
  ```
  user_id      BIGINT
  username     TEXT
  full_name    TEXT
  group_id     BIGINT
  group_name   TEXT
  agreed_at    TIMESTAMPTZ
  coc_version  TEXT
  PRIMARY KEY (user_id, group_id, coc_version)
  ```
- [x] Implement helper functions:
  ```python
  def record_agreement(user, group, version): ...
  def has_agreed(user_id, group_id, version): ...
  def has_agreed_anywhere(user_id, version): ...  # for cross-group fast-path
  def get_all_agreed(group_id, version): ...
  ```

---

## 3. Gatekeeper (Core Enforcement)

Triggered on every message in a managed group.

- [ ] Check `has_agreed(user_id, group_id, current_version)`
- [ ] If not agreed:
  1. Delete message immediately
  2. Restrict user (`can_send_messages=False`)
  3. Attempt DM with CoC and Agree button
  4. If DM fails (user has privacy settings blocking unknown bots): post inline message in the group tagging the user with the Agree button
- [ ] If agreed: do nothing, message stands

**Note:** Telegram delivers messages to all clients before the bot can delete them (~0.5–2s window). Mobile push notifications will have already fired with the message content. This is a hard API limitation — delete-fast is the only option.

---

## 4. New Member Join

Triggered by `ChatMemberHandler` when a user joins.

- [ ] Immediately restrict user (`can_send_messages=False`)
- [ ] Attempt DM with CoC and Agree button
- [ ] If DM fails: post inline message in group tagging the user

---

## 5. Cross-Group Identity (Hybrid)

Users who are in multiple groups should not have to read the full CoC repeatedly.

- [ ] On gatekeeper/join trigger: call `has_agreed_anywhere(user_id, current_version)`
- [ ] If they have agreed in another group: send lightweight confirm message — "You've already agreed to the CoC in another group. Tap to confirm it applies here too." (one button, no re-reading required)
- [ ] On confirm: record agreement for this group and unrestrict
- [ ] If they have never agreed anywhere: run full CoC flow

---

## 6. Agree Callback

Triggered when user taps any Agree or Confirm button.

- [ ] Record agreement to PostgreSQL (`record_agreement()`)
- [ ] Unrestrict user in the relevant group (`can_send_messages=True`, restore all permissions)
- [ ] Confirm to user ("You're all set, you can now post in [group name]")

---

## 7. Admin Commands

All commands restricted to user IDs in `ADMIN_IDS`.

| Command | Description |
|---|---|
| `/whoagreed` | List users who have agreed to the current CoC version in this group |
| `/setversion <v>` | Bump CoC version — all users must re-agree |
| `/post_onboarding` | Post a pinnable message with an Agree button (permanent anchor for users to self-serve) |

---

## 8. Railway Deployment

- [ ] Use webhooks (not polling) — Railway provides a persistent public HTTPS URL
- [ ] Set `WEBHOOK_URL` to the Railway-assigned URL
- [ ] Create `Procfile` or `railway.toml` to define start command
- [ ] PostgreSQL data persists across deploys via Railway plugin (no ephemeral filesystem risk)
- [ ] Bot restarts automatically on crash via Railway's always-on service

---

## 9. Known Constraints to Handle

- [ ] **Delete race condition**: Message is visible ~0.5–2s and push notifications fire before delete. Acceptable, not fixable.
- [ ] **DM blocked**: Implement group fallback (inline message tagging user) as described in §3
- [ ] **Bot permissions**: Must be admin in each group with "Delete messages" + "Restrict members" enabled
- [ ] **DRY_RUN mode**: Log all actions without actually restricting users or deleting messages — for safe production testing

---

## 10. Testing

- [ ] Create private test group with test accounts
- [ ] Verify gatekeeper: message deleted, user restricted, DM sent
- [ ] Verify DM-blocked fallback: inline group message appears
- [ ] Verify Agree flow: user unrestricted after tap
- [ ] Verify new member join: immediate restriction + DM
- [ ] Verify cross-group fast-path: confirm-only flow for known users
- [ ] Verify `/setversion` forces re-agreement for all users
- [ ] Verify admin commands reject non-admin users
- [ ] Verify PostgreSQL writes persist across Railway redeploy
