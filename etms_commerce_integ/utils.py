import frappe


def eci_log_error(content=None):
    tb = frappe.get_traceback()
    doc = {
        "doctype": "ECI Error Logs",
        "content": content or tb
    }

    log = frappe.get_doc(doc)
    log.flags.ignore_permissions = True
    log.insert()


def get_item_price(item_code):
    eci_settings = frappe.get_single("ECI Commerce Settings")
    item_price = 0

    price_list = ""

    try:
        if frappe.session.user == "Guest":
            price_list = eci_settings.guest_user_price_list
        else:
            price_list = frappe.get_all("Customer",
                                        fields="*",
                                        filters={"name": frappe.session.user
                                                })[0]["default_price_list"]

        pl = frappe.get_all("Item Price",
                            fields=["price_list_rate"],
                            filters={
                                "item_code": item_code,
                                "price_list": price_list,
                                "selling": True,
                            })

        if len(pl) > 0:
            item_price = pl[0]["price_list_rate"]

        return item_price
    except Exception as e:
        eci_log_error()
        return item_price

@frappe.whitelist(allow_guest=True)
def get_item_quantity(item_code, warehouse=None):
    conds = {"item_code": item_code}
    total_quantity = 0

    if warehouse:
        conds["warehouse"] = warehouse

    bins = frappe.get_all("Bin", fields=["actual_qty"], filters=conds)

    for bin in bins:
        total_quantity += bin["actual_qty"]
    
    return total_quantity