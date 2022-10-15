import frappe
from frappe.utils import now
from etms_commerce_integ.customer import get_customer_vehicles
from etms_commerce_integ.auth import eci_verify_request, eci_log_error


@frappe.whitelist(allow_guest=True, methods=["GET"])
@eci_verify_request
def get_next_ad():
    # display_order = frappe.form_dict["display_order"]
    try:
        datetime_now = now()
        sched_ads = frappe.get_all(
            "ECI Scheduled Advertisements",
            fields=["parent"],
            filters={
                "display_from": ("<", datetime_now),
                "display_to": (">", datetime_now),
            }
        )

        ads = []
        for sch_ad in sched_ads:
            _ads = frappe.get_all("ECI Advertisements",
                                fields=["name", "ad_image", "display_order"],
                                filters={
                                    "name": sch_ad.parent,
                                    "enabled": True,
                                },
                                order_by="display_order asc")
            for ad in _ads:
                # get ad targeted advertisement
                targeted_customer_vehicles =  frappe.get_all(
                    "ECI Advertisements Targeted Customer Vehicles Table",
                    fields=["vehicle_make", "vehicle_model", "vehicle_year"],
                    filters={"parent": ad.name}
                )

            if len(targeted_customer_vehicles) > 0:
                for targeted_customer_vehicle in targeted_customer_vehicles:
                    customer_vehicles = get_customer_vehicles.__wrapped__(customer=frappe.session.user)

                    for customer_vehicle in customer_vehicles:
                        if (targeted_customer_vehicle["vehicle_make"] == customer_vehicle["vehicle_make"]
                        and targeted_customer_vehicle["vehicle_model"] == customer_vehicle["vehicle_model"]
                        and targeted_customer_vehicle["vehicle_year"] == customer_vehicle["vehicle_year"]):
                            ads.append(ad)
                            break

                        elif (targeted_customer_vehicle["vehicle_make"] == customer_vehicle["vehicle_make"]
                        and targeted_customer_vehicle["vehicle_model"] == customer_vehicle["vehicle_model"]
                        and (targeted_customer_vehicle["vehicle_year"] == None or len(targeted_customer_vehicle["vehicle_year"]) == 0) ):
                            ads.append(ad)
                            break
                        elif (targeted_customer_vehicle["vehicle_make"] == customer_vehicle["vehicle_make"]
                        and (targeted_customer_vehicle["vehicle_model"] == None or len(targeted_customer_vehicle["vehicle_model"]) == 0)
                        and (targeted_customer_vehicle["vehicle_year"] == None or len(targeted_customer_vehicle["vehicle_year"]) == 0)):
                            ads.append(ad)
                            break                    
            else:
                ads.append(ad)
        return ads
    except:
        eci_log_error()
        print(frappe.get_traceback())
