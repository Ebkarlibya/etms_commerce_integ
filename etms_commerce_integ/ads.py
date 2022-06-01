import frappe
from etms_commerce_integ.auth import eci_verify_request
from etms_commerce_integ.auth import eci_log_error


@frappe.whitelist(allow_guest=False, methods=["GET"])
@eci_verify_request
def get_ads():

    pass