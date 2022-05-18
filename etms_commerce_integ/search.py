import frappe
from etms_commerce_integ.auth import eci_verify_request
from frappe.desk.search import validate_and_sanitize_search_inputs


@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_vehicle_compatibility():
    filters = []
    fieldname = frappe.form_dict['fieldname']
    compat_doctypes = {
        "make": "ECI Vehicle Make",
        "model": "ECI Vehicle Model",
        "year": "ECI Vehicle Year"
    }

    term = frappe.form_dict['term']
    selected_make = frappe.form_dict['selected_make']

    if term:
        filters.append([fieldname, 'like', f'%{term}%'])

    if selected_make:
        filters.append(['parent_compat', '=', selected_make])

    result = frappe.get_all(compat_doctypes[fieldname],
                            fields=fieldname,
                            filters=filters,
                            order_by=f"{fieldname} asc")

    return result

@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_product_brands():

    brands = frappe.get_all("Brand",
                                 fields=["name"],
                                )

    return brands

@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_territories():

    territories = frappe.get_all("Territory",
                                 fields=["name"],
                                 filters={"is_group": False})

    return territories


@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_payment_methods():

    payment_methods = frappe.get_all("Mode of Payment",
                                 fields=["name"],
                                 filters={"enabled": True}
                                )

    return payment_methods
