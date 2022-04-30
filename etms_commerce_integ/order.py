from datetime import datetime
import frappe
from etms_commerce_integ.auth import eci_verify_request
from erpnext.stock.get_item_details import get_item_details
from numpy import double
# from frappe.utils.formatters import format_datetime

# format_datetime("datetime.datetime(2022, 4, 30, 11, 15, 46, 645825)")
# datetime.datetime(2022, 4, 30, 11, 15, 46, 645825)
@frappe.whitelist(allow_guest=False, methods=["POST"])
@eci_verify_request
def checkout():
    eci_settings = frappe.get_single("ECI Commerce Settings")
    customer = frappe.get_doc("Customer", frappe.session.user)
    line_items = frappe.form_dict['line_items']

    # prepare items
    items = []
    for item in line_items:
        item_details = get_item_details({
            "item_code": "itm-0004",
            "company": "ETMS",
            "doctype": "Sales Order",
            "conversion_rate": 1,
            "price_list": "Standard Selling"
        })
        items.append({
            "item_code": item['product_id'],
            "rate": item_details['valuation_rate'],
            "delivery_date": datetime.now(),
            "qty": item['quantity'],
            # "warehouse": woocommerce_settings.warehouse
        })
    try:
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer.name,
            "customer_group": eci_settings.default_customer_group,
            "delivery_date": datetime.now(),
            "company": eci_settings.default_company,
            "selling_price_list": eci_settings.default_price_list,
            "ignore_pricing_rule": 1,
            "items": items,
            # disabled discount as WooCommerce will send this both in the item rate and as discount
            #"apply_discount_on": "Net Total",
            #"discount_amount": flt(woocommerce_order.get("discount_total") or 0),
            "currency": eci_settings.default_currency,
            "is_eci_order": 1
            # "taxes_and_charges": tax_rules,
            # "customer_address": billing_address,
            # "shipping_address_name": shipping_address
            # TODO SHIPPING ADDR
        })
        frappe.flags.ignore_permissions = True
        so.insert()

        return {"message": "your_order_accepted"}
    except Exception as e:
        print(e)
        frappe.throw(e.args)


@frappe.whitelist(allow_guest=False, methods=['GET'])
@eci_verify_request
def customer_orders():

    _orders = frappe.get_all("Sales Order",
                                     fields=[
                                         "name",
                                         "status",
                                         "total",
                                         "total_qty"
                                        ],
                                     filters={
                                         "customer": frappe.session.user,
                                         "is_eci_order": 1
                                     })
    customer_orders = []

    for order in _orders:
        customer_orders.append(
            {
                "id": order.name,
                "delivery_status": "working",
                "shipping": order.shipping_address,
                "status": order.status,
                "quantity": int(order.total_qty),
                "total": float(order.total),
            }
        )
    return customer_orders


# @frappe.whitelist(allow_guest=False, methods=['GET'])
# @eci_verify_request
# def customer_order_notes():

#     return [
#         {
#             "id": 1,
#             "date_created": "2020-05-01",
#             "note": "a note"
#         }
#     ]