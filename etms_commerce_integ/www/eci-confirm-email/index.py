import frappe


def get_context(ctx):
    ctx.no_cache = 1

    confirm_key = frappe.form_dict["key"]

    target_customer= frappe.get_value(
        "Customer", filters={"eci_email_confirmation_key": confirm_key})
    
    if target_customer:
        customer = frappe.get_doc("Customer", target_customer)
        customer.eci_is_customer_email_verified = True
        customer.eci_email_confirmation_key = ""

        customer.flags.ignore_mandatory = True
        customer.flags.ignore_permissions = True
        customer.save()
        frappe.db.commit()

        ctx["is_valid"] = True
        ctx["user_email"] = target_customer
    else:
        ctx["is_valid"] = False
