#!/usr/bin/env python3
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import logging
import json
import os

from flask import Flask, request

# Enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initial Flask app
app = Flask(__name__)
HOOK_URL = os.environ['HOOK_URL']


@app.route('/alert', methods=['POST'])
def alert():
    content = request.get_json()
    try:
        alert_status = content['status']
        if alert_status == "firing":
            theme_color = "d63333"
        else:
            theme_color = "64a837"

        sections = []
        for alert in content['alerts']:
            if 'description' in alert['annotations']:
                description = alert['annotations']['description']
            else:
                description = None
            if 'summary' in alert['annotations']:
                summary = alert['annotations']['summary']
            else:
                summary = None
            if 'runbook_url' in alert['annotations']:
                runbook_url = alert['annotations']['runbook_url']
            else:
                runbook_url = None
            if alert['status'] == "firing":
                activity_image = "https://img.icons8.com/external-wanicon-flat-wanicon/64/000000/external-fire-nature-wanicon-flat-wanicon.png"
            else:
                activity_image = "https://img.icons8.com/color/144/000000/ok--v1.png"

            labels = ""
            for label in alert['labels']:
                labels += f" {label}: `{alert['labels'][label]}`<br/>"

            section = {
                "activityTitle": alert['labels']['alertname'],
                "activitySubtitle": alert['status'],
                "activityImage": activity_image,
                "facts": [
                    {
                        "name": "Summary",
                        "value": summary
                    },
                    {
                        "name": "Description",
                        "value": description
                    },
                    {
                        "name": "Runbook Url",
                        "value": runbook_url
                    },
                    {
                        "name": "Labels",
                        "value": labels
                    }
                ],
                "markdown": "true"
            }
            sections.append(section)

        message = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": theme_color,
            "summary": "Alertmanager Alerts",
            "sections": sections
        }

        req = Request(HOOK_URL, json.dumps(message).encode('utf-8'))
        try:
            response = urlopen(req)
            response.read()
            logger.info("Message posted")
        except HTTPError as e:
            logger.error("Request failed: %d %s", e.code, e.reason)
        except URLError as e:
            logger.error("Server connection failed: %s", e.reason)
    except Exception as e:
        logger.error(e)
    return 'ok'


if __name__ == "__main__":
    # Running server
    app.run(host='0.0.0.0', port=9165)
