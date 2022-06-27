from typing import List
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
def get_item_quantity(item_code: str):
    """ Get Item Stock Level including ECI Multi Vendor """
    item_total_qty = 0

    # Warehouses to check Item Availability
    warehouse_to_check = frappe.get_all("ECI Publish Warehouses Table", 
                    fields=["warehouse"],
                    filters={"parent": item_code}
                )
    # Warehouses to check Item Availability (Supplier)
    supplier_warehouse_to_check = []
    if frappe.db.get_value("Item", filters={"item_code": item_code}, fieldname="eci_check_availability_in_suppliers_warehouse"):
        supplier_warehouse_to_check = frappe.get_all("ECI Supplier Warehouse Table", 
                    fields=["supplier_warehouse"],
                    filters={"parent": item_code}
                )
        for sw_to_check in supplier_warehouse_to_check:
            # get last supplier warehouse inventory
            sinv = frappe.get_all("ECI Supplier Inventory",
                        fields=["quantity"],
                        filters={
                            "product": item_code,
                            "supplier_warehouse": sw_to_check.supplier_warehouse
                        },
                        order_by="modified desc"
                        )
            if len(sinv) > 0:
                item_total_qty += sinv[0].quantity

    # if one of them not empty the product is sellable 
    if len(warehouse_to_check) > 0 or len(supplier_warehouse_to_check) > 0:
        for wh in warehouse_to_check:

            bins = frappe.get_all("Bin", 
                            fields=["actual_qty"],
                            filters={
                                "item_code": item_code, "warehouse": wh.warehouse
                            })

            for bin in bins:
                item_total_qty += bin.actual_qty
        
        return item_total_qty
    else:
        return None

@frappe.whitelist(allow_guest=True)
def get_warehouse_item_quantity(item_code: str, warehouse: str):
    """ Get Item Stock Level including ECI Multi Vendor """
    item_total_qty = 0


    sinv = frappe.get_all("ECI Supplier Inventory",
                fields=["quantity"],
                filters={
                    "product": item_code,
                    "supplier_warehouse": warehouse
                },
                order_by="modified desc"
                )
    if len(sinv) > 0:
        item_total_qty += sinv[0].quantity


    bins = frappe.get_all("Bin", 
                    fields=["actual_qty"],
                    filters={
                        "item_code": item_code,
                        "warehouse": warehouse
                    })
    if len(sinv) == 0 and len(bins) == 0:
        return None

    for bin in bins:
        item_total_qty += bin.actual_qty

    return item_total_qty


def get_item_warehouses(item_code: str, mode: int = 0):
    """
        get a specific item warehouses
        mode is the fetch modes:
        0: fetch item warehouses from erpnext + eci multi vendor 
        1: fetch item warehouses of erpnext
        2: fetch item warehouses of eci multi vendor
        
    """
    
    item_warehouses = []
    
    if mode == 0:
        bins = frappe.db.sql("""
            select warehouse from `tabBin` b where b.item_code = %(item_code)s
        """, {"item_code": item_code}, as_dict=False)

        # get eci supplier item warehouses
        supplier_inventories = frappe.db.sql("""
            select supplier_warehouse from `tabECI Supplier Inventory` sinv
            where product = %(item_code)s
            group by supplier_warehouse
            order by modified desc
        """, {"item_code": item_code}, as_dict=False)

        _zip = bins + supplier_inventories
        
        for w in _zip:
            item_warehouses.append(w[0])

        return item_warehouses
    elif mode == 1:
        bins = frappe.db.sql("""
            select warehouse from `tabBin` b where b.item_code = %(item_code)s
        """, {"item_code": item_code}, as_dict=False)
        
        for w in bins:
            item_warehouses.append(w[0])

        return item_warehouses
    elif mode == 2:
        supplier_inventories = frappe.db.sql("""
            select supplier_warehouse from `tabECI Supplier Inventory` sinv
            where product = %(item_code)s
            group by supplier_warehouse
            order by modified desc
        """, {"item_code": item_code}, as_dict=False)
        
        for w in supplier_inventories:
            item_warehouses.append(w[0])

        return item_warehouses

@frappe.whitelist(allow_guest=True)
def get_item_stock_levels(item_code: str, warehouse: str = None):
    stock_levels = []

    item_warehouses = get_item_warehouses(item_code, 2)

    if not warehouse:
        for itm_wh in item_warehouses:
            warehouse_quantity = get_warehouse_item_quantity(item_code, itm_wh)
            stock_levels.append(
                {
                    "warehouse": itm_wh,
                    "quantity": warehouse_quantity
                }
            )
        return stock_levels
    else:
        warehouse_quantity = get_warehouse_item_quantity(item_code, warehouse)
        if not warehouse_quantity:
            return None
        stock_levels.append(
            {
                "warehouse": warehouse,
                "quantity": warehouse_quantity
            }
        )
        return stock_levels

def get_warehouse_delivery_days(warehouse: str, territory: str):
    # get erpnext warehouse territory expected delivery days
    delivery_days = frappe.get_all("ECI Warehouse Expected Delivery Date Table",
                            fields=["expected_delivery_days"],
                            filters={
                                "parent": warehouse,
                                "territory": territory
                            })
    if len(delivery_days) > 0:    
        return delivery_days[0].expected_delivery_days
    else:
        return None