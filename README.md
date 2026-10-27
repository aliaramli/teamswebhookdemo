# RTO Teams Notification

A small Flask webpage with one `RTO` button. Selecting it posts `Alia will RTO today, <today's date>` to the configured Microsoft Teams channel using an incoming webhook.

## Setup

1. In Microsoft Teams, add and configure an Incoming Webhook (or the Workflows webhook trigger) for the target channel, then copy its URL.
2. Create a file named `.env` next to `app.py` and copy the values from `.env.example`.
3. Set `TEAMS_WEBHOOK_URL` in `.env` to the URL from Teams.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

5. Install dependencies and start the app:

   ```powershell
   pip install -r requirements.txt
   python app.py
   ```

Open http://127.0.0.1:5000 in a browser.

## Notes

- The webhook URL stays on the server and is not sent to the browser.
- Incoming webhooks are scoped to one Teams channel. To target a different channel, configure its webhook URL in `.env`.
- If your organization disables incoming webhooks, use a Teams Workflows webhook that accepts a JSON `text` field, or replace `send_to_teams` with Microsoft Graph API authentication.
- The app uses the Windows system certificate store, which supports company-managed root certificates for Teams HTTPS traffic.

## Corporate Certificate Support

Some corporate Windows networks use a company-managed certificate authority for HTTPS traffic. Python's default certificate bundle may not recognize that authority, preventing the app from connecting to the Teams webhook.

This app uses the `truststore` package to trust the Windows system certificate store when sending webhook requests. The required package is installed with the other dependencies, so no additional configuration is needed. This resolves Teams connection and certificate errors on Windows machines managed by an organization.