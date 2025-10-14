## 🧱 **Detailed Developer Task Breakdown**

### **1. Setup & Configuration**

**Tasks:**

* [ ] Create a new bot via [@BotFather](https://t.me/BotFather), get token.
* [ ] Create a Google Service Account and share the target Google Sheet with it (Editor access).
* [ ] Store Google credentials securely (JSON file).
* [ ] Set up environment variables:

  ```
  BOT_TOKEN=<telegram-bot-token>
  SHEET_ID=<google-sheet-id>
  ADMIN_IDS=<comma-separated-admin-ids>
  COC_VERSION=1.0
  COC_LINK=https://example.com/code-of-conduct
  ```

---

### **2. Integrate Google Sheets**

**Tasks:**

* [ ] Connect to Google Sheets via `gspread`.
* [ ] Create a worksheet named `Agreements` with headers:

  ```
  user_id | username | full_name | group_id | group_name | agreed_at | coc_version
  ```
* [ ] Implement helper functions:

  ```python
  def record_agreement(user, group, version): ...
  def has_agreed(user_id, group_id, version): ...
  def get_all_agreed(group_id, version): ...
  def get_all_not_agreed(group_id, version): ...
  ```

---

### **3. Bot Core Features**

**Tasks:**

* [ ] Implement `/start` command:

  * Sends CoC message with **Agree** button.
* [ ] Implement `CallbackQueryHandler` for “Agree” button.

  * Logs data to Google Sheet.
  * Unrestricts user in group.
* [ ] Implement `ChatMemberHandler` for `new_chat_members` event:

  * Restricts user.
  * Sends onboarding message.
* [ ] Implement error handling (e.g., if bot cannot DM user, fallback to inline message).

---

### **4. Admin Features**

**Tasks:**

* [ ] Implement `/whoagreed` → Query Google Sheet and return list/count.
* [ ] Implement `/whohasnotagreed` → List of members missing.
* [ ] Implement `/sendcode` → Re-sends CoC message to all (or to users without agreement).
* [ ] Implement `/setversion` → Updates global CoC version and resets state.
* [ ] Restrict all admin commands to user IDs in `ADMIN_IDS`.

---

### **5. Permissions Handling**

**Tasks:**

* [ ] On join, use `restrict_chat_member` to disable messaging.
* [ ] On agreement, use `restrict_chat_member` with full permissions to restore.
* [ ] Optional: After X days, restrict users who haven’t agreed yet.

---

### **6. Optional Enhancements**

**Tasks:**

* [ ] Add a `/status` command so users can check if they’ve agreed.
* [ ] Add multi-language support.
* [ ] Schedule daily/weekly report to admin (e.g., 3 users haven’t agreed yet).
* [ ] Use inline keyboards with “View Code of Conduct 📜” and “Agree ✅” buttons.
* [ ] Add simple analytics tab in Google Sheets.

---

### **7. Testing**

**Tasks:**

* [ ] Test joining workflow in a private test group.
* [ ] Test agreeing via DM and inline button.
* [ ] Test all admin commands.
* [ ] Test Google Sheets writes and reads.
* [ ] Verify permission enforcement (restricted/unrestricted).

---

### **8. Deployment**

**Tasks:**

* [ ] Choose hosting (PythonAnywhere / Render / VPS).
* [ ] Configure bot to run via `webhook` (for performance) or `polling` (simpler).
* [ ] Add bot as admin in target groups.
* [ ] Verify group permissions.
* [ ] Document environment variables and setup steps in README.

---

## 🧾 Deliverables

1. Working Python script for the bot.
2. `.env` configuration file template.
3. Google Sheet connection working.
4. Admin documentation (commands + setup).
5. Deployment instructions.

---

Would you like me to now **draft the Google Sheets structure and API integration code** (so your developer can plug it in directly)?
It would include:

* Ready-made `gspread` integration module.
* `record_agreement()` and `has_agreed()` helper functions.
