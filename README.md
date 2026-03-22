# Berkeley Application Status Monitor 🐻

Many applicants have been manually checking the Berkeley Astro portal every single day to see if they got in or if their status has been updated. 

This simple Python app will automatically sign you in every 30 minutes, check the portal in the background, and push a notification to your phone or computer via Discord or Email as soon as your status changes.

## Features
- **Auto-Login:** Safely signs in to the UC Berkeley CAS system automatically.
- **Cache-Busting:** Every single check is done on a clean browser profile (incognito style) so it doesn't accidentally read an old cached page.
- **Zero-Spam:** The second it detects a change, it sends one update and shuts itself down.
- **Debug Mode:** You can toggle a switch to watch the browser work on your screen, which is helpful if something gets stuck.
- **Secure:** All your info is saved locally to a `settings.json` file which is completely ignored by Git. Your passwords and webhooks never leave your machine.

## How to Install

1. Make sure you have [Python](https://www.python.org/downloads/) installed.
2. Clone this repo or download the files to a folder on your computer.
3. Open your terminal in that folder and run the following commands to install the required stuff:
   ```bash
   pip install playwright customtkinter requests resend
   python -m playwright install chromium
   ```
   *(Note: If you get an error saying `playwright is not recognized...`, using `python -m playwright` as shown above fixes it by running it directly through Python!)*

## How to Use

Just run the following command to start the app:
```bash
python gui_monitor.py
```

A clean GUI will pop up asking for:
1. **Berkeley Email:** The email you use to login to Berkeley.
2. **Berkeley Password:** The password for that email.
3. **Where to Notify You:** This is where you configure how you get alerted. 

***

## Getting Notified (Pick At Least One)

There are 2 places where you can receive updates. You can use both if you want to be extra sure, but only one is required!

### 1. Discord Webhook (Recommended & Easiest)
This sends a direct push notification to a Discord server. 

**How to get a Discord Webhook URL:**
1. Open Discord and make a brand-new free server just for yourself (click the `+` on the left sidebar).
2. Right-click the `#general` text channel and click **Edit Channel**.
3. Go to the **Integrations** tab on the left.
4. Click **Webhooks**, then **New Webhook**.
5. Click **Copy Webhook URL** and paste that link directly into the app!
*(Make sure your phone notifications are turned on for your new server!)*

### 2. Email via Resend.com
This sends a standard email directly to the Berkeley email address you put in the first box.

**How to get a Resend API Key:**
1. Go to [Resend.com](https://resend.com/) and make a free account.
2. Once you are on the dashboard, navigate to the **API Keys** section.
3. Generate a new API Key, copy it, and paste it directly into the app!
*(Note: Because you are on a free tier, Resend will only let you send emails back to the exact same email address you used to sign up for Resend. Ensure your Berkeley email is the one you sign up with!)* 

***

That's it. Just hit **Start Monitoring** and let it run.
