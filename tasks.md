# Developer Task Breakdown

## 1. Setup & Configuration

- [x] Create bot via [@BotFather](https://t.me/BotFather), get token
- [x] Create Railway project, add PostgreSQL plugin
- [x] Configure environment variables (WEBHOOK_URL set after first deploy):
  ```
  BOT_TOKEN=<telegram-bot-token>
  ADMIN_IDS=<comma-separated-admin-user-ids>
  COC_VERSION=1.0
  COC_LINK=https://icedippers.com/code-of-conduct
  COC_LINK_DE=https://icedippers.com/de/verhaltenskodex
  DATABASE_URL=<railway-postgres-url>
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
- [x] Create `settings` table on startup (stores active CoC version and any future bot-wide config):
  ```
  key    TEXT PRIMARY KEY
  value  TEXT
  ```
- [x] Implement helper functions:
  ```python
  def record_agreement(user, group, version): ...
  def has_agreed(user_id, group_id, version): ...
  def has_agreed_anywhere(user_id, version): ...  # for cross-group fast-path
  def get_all_agreed(group_id, version): ...
  def get_setting(key, default): ...
  def set_setting(key, value): ...
  ```

---

## 3. Gatekeeper (Core Enforcement)

Triggered on every message in a managed group.

- [x] Check `has_agreed(user_id, group_id, current_version)`
- [x] If not agreed:
  1. Delete message immediately
  2. Restrict user (`can_send_messages=False`)
  3. Check `has_agreed_anywhere` — send fast-path confirm if true, full CoC DM if false
  4. If DM fails (user has privacy settings blocking unknown bots): post inline message in the group tagging the user
- [x] If agreed: do nothing, message stands
- [x] All user-facing messages are bilingual (English + German)

**Note:** Telegram delivers messages to all clients before the bot can delete them (~0.5–2s window). Mobile push notifications will have already fired with the message content. This is a hard API limitation — delete-fast is the only option.

---

## 4. New Member Join

Triggered by `ChatMemberHandler` when a user joins.

- [x] Immediately restrict user (`can_send_messages=False`)
- [x] Check `has_agreed_anywhere` — send fast-path confirm if true, full CoC DM if false
- [x] If DM fails: post inline message in group tagging the user
- [x] All user-facing messages are bilingual (English + German)

---

## 5. Cross-Group Identity (Hybrid)

Users who are in multiple groups should not have to read the full CoC repeatedly.

- [x] On gatekeeper/join trigger: call `has_agreed_anywhere(user_id, current_version)`
- [x] If they have agreed in another group: send lightweight confirm message with a single "Confirm / Bestätigen ✅" button
- [x] On confirm: record agreement for this group and unrestrict
- [x] If they have never agreed anywhere: run full CoC flow (two CoC link buttons EN/DE + Agree / Zustimmen button)

---

## 6. Agree Callback

Triggered when user taps any Agree or Confirm button.

- [x] Record agreement to PostgreSQL (`record_agreement()`)
- [x] Unrestrict user in the relevant group (`can_send_messages=True`, restore all permissions)
- [x] Confirm to user with bilingual success message including the group name

---

## 7. Admin Commands ✅

All commands restricted to user IDs in `ADMIN_IDS`.

| Command | Description |
|---|---|
| `/whoagreed` | List users who have agreed to the current CoC version in this group |
| `/setversion <v>` | Bump CoC version — stored in PostgreSQL, takes effect immediately without restart |
| `/post_onboarding` | Post a pinnable bilingual message with a permanent Agree button |

---

## 8. Railway Deployment ✅

- [x] Create `Procfile` with `web: python bot.py` (web process type so Railway assigns a public port)
- [x] PostgreSQL data persists across deploys via Railway plugin (no ephemeral filesystem risk)
- [x] Bot restarts automatically on crash via Railway's always-on service
- [x] Webhooks when `WEBHOOK_URL` is set (uses bot token as URL path for basic auth); falls back to polling for local dev

---

## 9. Known Constraints (all handled)

- [x] **Delete race condition**: Message is visible ~0.5–2s and push notifications fire before delete. Acceptable, not fixable.
- [x] **DM blocked**: Group fallback implemented — inline message tagging user posted in the group
- [x] **Bot permissions**: Documented — must be admin with "Delete messages" + "Restrict members"
- [x] **DRY_RUN mode**: Implemented — logs all actions without restricting or deleting

---

## 10. Testing

- [ ] Create private test group with test accounts
- [ ] Verify gatekeeper: message deleted, user restricted, bilingual DM sent
- [ ] Verify DM-blocked fallback: bilingual inline group message appears
- [ ] Verify Agree flow: user unrestricted, bilingual success confirmation shown
- [ ] Verify new member join: immediate restriction + bilingual DM
- [ ] Verify cross-group fast-path: confirm-only flow for known users
- [ ] Verify `/setversion` updates immediately (no restart) and forces re-agreement
- [ ] Verify admin commands reject non-admin users
- [ ] Verify PostgreSQL writes persist across Railway redeploy
