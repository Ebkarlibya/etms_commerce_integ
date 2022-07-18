import frappe
from etms_commerce_integ.customer import get_customer_vehicles
from etms_commerce_integ.auth import eci_verify_request, eci_log_error


@frappe.whitelist(allow_guest=True, methods=["GET"])
@eci_verify_request
def get_next_ad():

    try:
        ads = []
        _ads = frappe.get_all("ECI Advertisements",
                            fields=["name", "ad_image", "display_order"],
                            filters={"enabled": True},
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
                    customer_vehicles = get_customer_vehicles.__wrapped__(customer="kechupdev@outlook.com")

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
    except Exception as e:
        eci_log_error()
