import frappe
from etms_commerce_integ.auth import eci_verify_request

@frappe.whitelist(allow_guest=False)
@eci_verify_request
def update_user_profile():
    user = frappe.get_doc("User", frappe.session.user)

    first_name = frappe.form_dict["first_name"]
    last_name =  frappe.form_dict["last_name"] 
    shipping_address_1 = frappe.form_dict["shipping_address_1"]
    shipping_city = frappe.form_dict["shipping_city"]
    shipping_country = frappe.form_dict["shipping_country"]

    user.first_name = first_name 
    user.last_name = last_name

    user.save()
    address = None
    if len(frappe.get_all("Address", filters={"name": f"{user.name}-Shipping"})) == 0:
        new_address = frappe.get_doc({
            "doctype": "Address",
            "address_title": user.name,
            "address_type": "Shipping",
            "address_line1": shipping_address_1,
            "city": shipping_city,
            "country": "Libya",
            "email_id": user.email,
            "phone": user.mobile_no
        })
        new_address.flags.ignore_mandatory = True
        new_address.flags.ignore_permissions = True
        new_address.insert()
        address = new_address
    else:
        address = frappe.get_doc("Address", f"{user.name}-Shipping")
        address.address_line1 = shipping_address_1
        address.city = shipping_city
        address.country = "Libya"
        address.flags.ignore_mandatory = True
        address.flags.ignore_permissions = True
        address.save()
    return {
        "id": user.name,
        "displayname": user.full_name,
        "name": user.name,
        "username": user.name,
        "firstname": user.first_name,
        "lastname": user.last_name,
        "email": user.email,
        "nicename": user.full_name,
        "url": "USER URL...",
        "roles": [],
        "address_line1": address.address_line1,
        "city": address.city,
        "message": "profile_updated"
    }
