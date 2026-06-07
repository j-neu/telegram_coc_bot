## 🧭 High-Level Project Overview

### 🎯 Goal
To ensure every group member, new or existing, explicitly agrees to the group's Code of Conduct (CoC) before being allowed to post messages.

### 🧩 Core Logic
1.  **Gatekeeper on All Messages**: The bot checks every message. If the sender has not agreed to the current CoC, their message is deleted, they are restricted, and the bot attempts to DM them.
2.  **Pinned Onboarding Message**: An admin uses `/post_onboarding` to create a persistent message with an "Agree" button. This message is pinned for all users to see.
3.  **Direct Agreement**: Any user can click the "Agree" button on the pinned message at any time. This records their agreement in the database and grants them speaking permissions.

This architecture is the most robust and user-friendly, as it provides a clear, single point of action for all users while enforcing the rules on anyone who tries to bypass it.

### 🏗️ Tech Stack
* **Language:** Python 3.10+
* **Libraries:** `python-telegram-bot`
* **Database:** SQLite

---

## 📋 Functional Requirements

### 1. New Member Onboarding
- When a new member joins, they are immediately restricted.
- The bot attempts to DM them with a welcome message, directing them to the pinned message in the group.

### 2. Existing Member Onboarding
- The primary mechanism is the **Gatekeeper**. When an existing member who has not agreed tries to talk, their message is deleted, and they are restricted.
- The pinned message created by `/post_onboarding` serves as the permanent, visible way for these users to agree and get unrestricted.

### 3. Admin Commands
| Command | Description |
|---|---|
| `/post_onboarding` | Posts the pinnable message for users to agree. |
| `/whoagreed` | Lists users who have agreed to the current CoC. |
| `/setversion <v>` | Sets a new CoC version, requiring all users to re-agree. |
