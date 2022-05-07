import frappe


def eci_log_error(title = "Error"):
    tb = frappe.get_traceback()
    log = frappe.get_doc({
        "doctype": "ECI Error Logs",
        "title": title,
        "content": tb
    })
    log.flags.ignore_permissions = True
    log.insert()