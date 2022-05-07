import frappe


def eci_log_error():
    tb = frappe.get_traceback()
    log = frappe.get_doc({
        "doctype": "ECI Error Logs",
        "content": tb
    })
    log.flags.ignore_permissions = True
    log.insert()