from dataclasses import field

from etms_commerce_integ.utils import eci_log_error
import frappe
from etms_commerce_integ.auth import eci_verify_request
from frappe.desk.search import validate_and_sanitize_search_inputs


@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_vehicle_compatibility():
    try:
        filters = []
        fieldname = frappe.form_dict['fieldname']
        term = frappe.form_dict['term']
        selected_make = frappe.form_dict['selected_make']

        compat_doctypes = {
            "make": "ECI Vehicle Make",
            "model": "ECI Vehicle Model",
            "year": "ECI Vehicle Year"
        }



        if term:
            filters.append([fieldname, 'like', f'%{term}%'])

        if selected_make and fieldname != 'year':
            filters.append(['parent_compat', '=', selected_make])

        result = frappe.get_all(compat_doctypes[fieldname],
                                fields=fieldname,
                                filters=filters,
                                order_by=f"{fieldname} asc")

        return result
    except:
        eci_log_error()
        print(frappe.get_traceback())
        
@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_product_brands():
    try:
        brands = frappe.get_all(
            "Brand",
            fields=["name"],
        )

        return brands
    except:
        eci_log_error()
        print(frappe.get_traceback())

@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_territories():
    try:
        territories = frappe.get_all("Territory",
                                    fields=["name"],
                                    filters={"is_group": False})

        return territories
    except:
        eci_log_error()
        print(frappe.get_traceback())

@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def search_payment_methods():
    try:
        payment_methods = frappe.get_all("Mode of Payment",
                                    fields=["name"],
                                    filters={"enabled": True}
                                    )

        return payment_methods
    except:
        eci_log_error()
        print(frappe.get_traceback())

@frappe.whitelist(allow_guest=True, methods=["POST"])
@eci_verify_request
def autocomplete_search():
    try:
        term = frappe.form_dict['term']

        sugesstions = frappe.get_all("ECI Product Tags",
                                fields=["name"],
                                filters=[
                                    ["name", "like", f"%{term}%"]
                                ],
                                limit_page_length=6)

        return sugesstions
    except:
        eci_log_error()
        print(frappe.get_traceback())