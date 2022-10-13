import onesignal
import frappe
import json
import hashlib
import requests
from onesignal.api import default_api
from onesignal.model.notification import Notification
from onesignal.model.create_notification_success_response import CreateNotificationSuccessResponse
from onesignal.model.create_notification_bad_request_response import CreateNotificationBadRequestResponse


# send notification to user via one signal
def ets_send_notification(message, username, data=None):

    try:
        external_user_id = hashlib.sha256(username.encode()).hexdigest()

        response = requests.post(
            url=f"https://onesignal.com/api/v1/notifications",
            json={
                # "included_segments": ["Subscribed Users"],
                # "subtitle": {"en": "subtitle test"},
                # "name": "جيد جدا",
                "contents": {"en": message},
                "data": data,
                "app_id": frappe.conf.osig_app_id,
                "include_external_user_ids": [external_user_id]
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Basic " + frappe.conf.osig_api_key
            }
        )

        if response:
            print(response.content)
        else:
            log_data = f"""
                url: {response.url}
                method: {response.request.method}
                status: {response.status_code}
                content: {response.content}
                reason: {response.reason}
                text: {response.text}
            """
            print(log_data)
            frappe.log_error(log_data, title="ECI Request Error")

            return None
    except Exception as e:
        print(e)
        frappe.log_error(log_data, title="ECI Error")
