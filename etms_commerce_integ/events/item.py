import frappe

def on_update(doc, method):
    if doc.publish_to_commerce_app:
        item_prices = frappe.get_all("Item Price",
                fields=["name"],
                filters={
                    "item_code": doc.item_code,
                    "selling": True
                })
        if len(item_prices) == 0:
            frappe.throw(frappe._(f"ECI: Cant Publish, Item {doc.item_name} has no <a target='_blank' href='/app/item-price'>item sell price</a>"))