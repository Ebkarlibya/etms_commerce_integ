import frappe
from etms_commerce_integ.auth import eci_verify_request
from etms_commerce_integ.auth import eci_log_error


@frappe.whitelist(allow_guest=False, methods=["POST"])
@eci_verify_request
def get_next_ad():
    display_order = frappe.form_dict['display_order']

    ads = frappe.get_all("ECI Advertisements",
                         fields=["ad_image", "display_order"],
                         filters={"enabled": True})

    if len(ads) == 0:
        return {"message": "no_ads"}

    next_ad = list(filter(lambda ad: ad.display_order == display_order, ads))

    if next_ad:
        return {"message": "next_ad", "data": next_ad[0]}
    else:
        return {"message": "reset_order"}