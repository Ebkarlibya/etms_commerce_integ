import frappe
from frappe.core.doctype.user.user import generate_keys
from frappe.core.doctype.user.user import User


@frappe.whitelist(allow_guest=True)
def user_info():
    print("asd")

@frappe.whitelist(allow_guest=True)
def login():
    usr = frappe.form_dict.get("username")
    pwd = frappe.form_dict.get("password")
    if usr and pwd:
        _user = User.find_by_credentials(usr, pwd)
        user = frappe.get_doc("User", _user.name)
        return {
            "user": user.name,
            "api_key": user.api_key,
            "api_secret": user.get_password("api_secret")
        }

        
    return "faild to login"