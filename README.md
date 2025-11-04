# 🚀 Finary Auto Signup (Gmail IMAP)

Automate the creation of multiple **Finary accounts** with referral support to get unlimited months of Finary Plus for free.
This script:

✅ Generates random first/last names
✅ Generates Gmail dot-trick emails (`e.m.ai.l@gmail.com`)
✅ Requests Finary signup & triggers OTP verification
✅ Connects to **Gmail IMAP** and extracts the **verification code automatically**
✅ Finalizes the signup + links crypto wallets to trigger bonus rewards 🚀

> ⚠️ Educational purpose only. Use responsibly.

---

## ✨ Features

| Feature                         | Description                                           |
| ------------------------------- | ----------------------------------------------------- |
| 🔐 Auto Gmail IMAP OTP fetch    | Reads the 6-digit OTP from Gmail (even in subject)    |
| 🟢 Fully automated signup       | No manual interaction needed                          |
| 🎭 Random identity generator    | Random first name, last name, password                |
| 🥷 Gmail dot trick exploitation | Generates new addresses without new inboxes           |
| 🪝 Referral support             | Credit referral code to your account                  |
| 💰 Auto-link accounts           | Automatically attaches wallets to complete onboarding |

---

## 📁 Project Structure

```
📦 /Finary-AutoSignup
 ┣ 📜 finarySignup.py     # Main automation script
 ┣ 📜 imapManager.py      # Gmail IMAP OTP extraction logic
 ┣ 📜 README.md           # You are here
```

---

## ✅ Requirements

### 1️⃣ Python dependencies

Install requirements:

```bash
pip install requests names
```

> `imaplib` and `email` are included in Python by default.

---

### 2️⃣ Gmail IMAP Configuration

1. Go to Gmail → **Settings → Forwarding & POP/IMAP → Enable IMAP**
2. Go to Google Security → **Create an App Password**
   🔗 [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Select: *Mail → Windows Computer*
4. Copy the generated password (16 chars, no spaces).

You will use this password as:

```
EMAIL_PASS = "abcd efgh ijkl mnop"   ❌ WRONG
EMAIL_PASS = "abcdefghijklmnop"      ✅ RIGHT
```

---

## 🚀 How to Use

1 Edit config values in the top of `finarySignup.py`:

```python
REFERRAL_CODE = "your finary referral here"
EMAIL_USER   = "yourgmail@gmail.com"
EMAIL_PASS   = "your_app_password_here"
```

2 Run the script:

```bash
python finarySignup.py
```

3 When prompted:

```
How many accounts do you want to create?
```

➡️ Enter any number (ex: 5)

The script will then:

* Generate a random Gmail dot-trick email
* Request OTP
* Automatically read Gmail inbox
* Verify account
* Link crypto wallets
* ✅ Done

---

## ⚠️ Disclaimer

This code is for **educational purposes only**.
By using this script, you agree:

* You are the owner of the Gmail inbox used
* You comply with Finary’s Terms of Service
* You do not abuse referral systems or create fraudulent accounts

Use responsibly. 🙏

---

## ⭐ Support the project

If you like this project:

* Star ⭐ the repo
* Fork it
* Improve it and PR back

---
