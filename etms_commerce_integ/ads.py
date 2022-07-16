import frappe
from etms_commerce_integ.auth import eci_verify_request
from etms_commerce_integ.auth import eci_log_error
from random import randint

# start at 10 and increment by 10
# display_order = 10


@frappe.whitelist(allow_guest=True, methods=["GET"])
@eci_verify_request
def get_next_ad():

    try:
        ads = frappe.get_all("ECI Advertisements",
                            fields=["enabled", "ad_image", "display_order"],
                            filters={"enabled": True},
                            order_by="display_order asc")


        ads_len = len(ads)
        if ads_len > 0:
            rand_ad = randint(0, ads_len - 1)
            return {"message": "next_ad", "data": ads[rand_ad]}
    except Exception as e:
        eci_log_error()

# @frappe.whitelist(allow_guest=True, methods=["GET"])
# @eci_verify_request
# def get_next_ad():

#     global display_order
#     ads = frappe.get_all("ECI Advertisements",
#                          fields=["enabled", "ad_image", "display_order"],
#                          order_by="display_order asc")


#     if len(ads) == 0:
#         return {"message": "no_ads"}

#     next_ad = list(filter(lambda ad: not ad.enabled == 0 and ad.display_order == display_order , ads))

#     if len(ads) > 0 and not next_ad and len(next_ad) > 0:
#         display_order = 10
#         return {"message": "end"}

#     if len(next_ad) == 0:
#         display_order += 10
#         return {"message": "end"}

#     display_order += 10

#     return {"message": "next_ad", "data": next_ad[0]}
