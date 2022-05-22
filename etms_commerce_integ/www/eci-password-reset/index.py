import frappe

def get_context(ctx):
    ctx.no_cache = 1


    reset_key = frappe.form_dict["key"]

    target_user = frappe.get_value("User", filters={"reset_password_key": reset_key})

    if target_user:
        # activate the user if not activated
        customer = frappe.get_doc("Customer", target_user)

        if not customer.eci_is_customer_email_verified:
            customer.eci_is_customer_email_verified = True
            customer.eci_email_confirmation_key = ""

            customer.flags.ignore_mandatory = True
            customer.flags.ignore_permissions = True
            customer.save()
            frappe.db.commit()

        ctx["is_valid"] = True
        ctx["user_email"] = target_user
    else:
        ctx["is_valid"] = False
