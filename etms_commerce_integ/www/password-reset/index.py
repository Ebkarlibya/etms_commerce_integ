import frappe

def get_context(ctx):
    ctx.no_cache = 1


    reset_key = frappe.form_dict["key"]

    target_user = frappe.get_value("User", filters={"reset_password_key": reset_key})

    if target_user:
        ctx["is_valid"] = True
        ctx["user_email"] = target_user
    else:
        ctx["is_valid"] = False
