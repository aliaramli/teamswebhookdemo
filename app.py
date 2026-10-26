import os
from datetime import datetime
from pathlib import Path

import truststore

truststore.inject_into_ssl()

import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "local-development-only")


class TeamsWebhookError(RuntimeError):
    """A webhook error that can be shown without exposing the URL."""


def build_teams_payload(message: str) -> dict:
    sent_at = datetime.now().astimezone().strftime("%d %b %Y, %H:%M %Z")
    return {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "contentUrl": None,
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.2",
                "body": [
                    {
                        "type": "Container",
                        "style": "emphasis",
                        "items": [{
                            "type": "TextBlock",
                            "text": "Channel update",
                            "size": "Medium",
                            "weight": "Bolder",
                            "wrap": True,
                        }],
                    },
                    {
                        "type": "Container",
                        "spacing": "Medium",
                        "items": [{
                            "type": "TextBlock",
                            "text": message,
                            "wrap": True,
                        }],
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Sent from Webhook Messenger | {sent_at}",
                        "spacing": "Medium",
                        "isSubtle": True,
                        "size": "Small",
                        "wrap": True,
                    },
                ],
            },
        }],
    }


def send_to_teams(message: str) -> None:
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("TEAMS_WEBHOOK_URL is not configured.")

    try:
        response = requests.post(webhook_url, json=build_teams_payload(message), timeout=10)
        response.raise_for_status()
    except requests.HTTPError as error:
        status_code = error.response.status_code if error.response is not None else "unknown"
        raise TeamsWebhookError(f"Teams returned HTTP {status_code}.") from error
    except requests.Timeout as error:
        raise TeamsWebhookError("Teams did not respond within 10 seconds.") from error
    except requests.RequestException as error:
        raise TeamsWebhookError("Could not connect to the Teams webhook.") from error


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        message = request.form.get("message", "").strip()

        if not message:
            flash("Enter a message before sending it.", "error")
        elif len(message) > 4_000:
            flash("Messages must be 4,000 characters or fewer.", "error")
        else:
            try:
                send_to_teams(message)
            except TeamsWebhookError as error:
                app.logger.exception("Teams webhook request failed")
                flash(str(error), "error")
            except RuntimeError as error:
                flash(str(error), "error")
            else:
                flash("Message sent to Teams.", "success")

        return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)