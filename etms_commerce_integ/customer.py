from re import I
import frappe
from etms_commerce_integ.auth import eci_verify_request
from etms_commerce_integ.auth import eci_log_error


@frappe.whitelist(allow_guest=False, methods=["GET"])
@eci_verify_request
def get_customer_vehicles(customer=None):
    vehicles = frappe.get_all(
        "ECI Customer Vehicles Table",
        fields=["idx", "name", "vehicle_make", "vehicle_model", "vehicle_year"],
        filters={"parent": customer or frappe.session.user},
        order_by="idx asc")

    return vehicles

@frappe.whitelist(allow_guest=False, methods=["POST"])
def save_customer_vehicle():
    try:
        vehicle_make = frappe.form_dict["vehicle_make"]
        vehicle_model = frappe.form_dict["vehicle_model"]
        vehicle_year = frappe.form_dict["vehicle_year"]
    
        customer_vehicles = None
        
        if len(frappe.get_all("ECI Customer Vehicles", filters={"name": frappe.session.user})) < 1:
            customer_vehicles = frappe.get_doc(
                {
                    "doctype": "ECI Customer Vehicles",
                    "customer": frappe.session.user
                }
            )
            customer_vehicles.flags.ignore_permissions=True
            customer_vehicles.insert()
        else:
            customer_vehicles = frappe.get_doc("ECI Customer Vehicles",
                                            frappe.session.user)

        row = customer_vehicles.append("customer_vehicles", {})
        row.vehicle_make = vehicle_make
        row.vehicle_model = vehicle_model
        row.vehicle_year = vehicle_year

        customer_vehicles.flags.ignore_permissions=True
        customer_vehicles.save()
        frappe.db.commit()

        vehicles = frappe.get_all(
            "ECI Customer Vehicles Table",
            fields=["name", "vehicle_make", "vehicle_model", "vehicle_year"],
            filters={"parent": frappe.session.user},
            order_by="idx asc")

        return {"message": "selected_vehicle_saved", "data": vehicles}
    except Exception as e:
        eci_log_error()


@frappe.whitelist(allow_guest=False, methods=["POST"])
def delete_customer_vehicle():
    try:
        name = frappe.form_dict["name"]

        frappe.db.delete(doctype="ECI Customer Vehicles Table", filters={
                                        "parent": frappe.session.user,
                                        "name": name
                                    }, debug=True,)
        vehicles = frappe.get_all(
            "ECI Customer Vehicles Table",
            fields=["name", "vehicle_make", "vehicle_model", "vehicle_year"],
            filters={"parent": frappe.session.user},
            order_by="idx asc")

        return {"message": "selected_vehicle_deleted", "data": vehicles}
    except Exception as e:
        eci_log_error()