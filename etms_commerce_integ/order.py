from datetime import date, datetime, timedelta
import re
from etms_commerce_integ.utils import get_item_quantity, get_item_warehouses, get_warehouse_delivery_days
from frappe.utils import add_to_date, now, nowdate
import frappe
from etms_commerce_integ.auth import eci_verify_request
from erpnext.stock.get_item_details import get_item_details
# from erpnext.stock.report.stock_balance.stock_balance import get_stock_ledger_entries


@frappe.whitelist(allow_guest=True, methods=['GET'])
@eci_verify_request
def get_shipping_cost():
    shipping_territory = frappe.form_dict["shipping_territory"]
    shipping_items = frappe.get_all("Item",
                                    fields=["standard_rate"],
                                    filters={
                                        "is_shipping_item": 1,
                                        "shipping_territory":
                                        shipping_territory
                                    })

    if shipping_items:
        return shipping_items[0]['standard_rate']
    return 0.0

@frappe.whitelist(allow_guest=False, methods=["POST"])
@eci_verify_request
def checkout():
    eci_settings = frappe.get_single("ECI Commerce Settings")
    customer = frappe.get_doc("Customer", frappe.session.user)
    line_items = frappe.form_dict["line_items"]
    shipping_territory = frappe.form_dict["shipping_territory"]
    shipping_address = frappe.form_dict["shipping_address"]
    mode_of_payment = frappe.form_dict["mode_of_payment"]
    # expected_delivery_time = frappe.form_dict["expected_delivery_time"]
    
    # prepare items
    items = []
    for item_code, qty in line_items.items():
        item_details = get_item_details({
            "item_code": item_code,
            "company": eci_settings.default_company,
            "doctype": "Sales Order",
            "conversion_rate": 1,
            "price_list": "Standard Selling"
        })
        items.append({
            "item_code": item_code,
            "rate": item_details['valuation_rate'],
            "margin_type": "",
            "delivery_date": datetime.now(),
            "qty": qty,
            # "warehouse": woocommerce_settings.warehouse
        })
    # add shipping item from territory
    # shipping_item = frappe.get_all("Item",
    #                                fields=["item_code", "standard_rate"],
    #                                filters={
    #                                    "is_shipping_item": 1,
    #                                    "shipping_territory": shipping_territory
    #                                })
    # shipping_item_details = get_item_details({
    #     "item_code": shipping_item[0].item_code,
    #     "company": eci_settings.default_company,
    #     "doctype": "Sales Order",
    #     "conversion_rate": 1,
    #     "price_list": "Standard Selling"
    # })
    # shipping item
    # items.append({
    #     "item_code": shipping_item[0].item_code,
    #     "rate": shipping_item[0].standard_rate,
    #     "margin_type": "",
    #     "delivery_date": datetime.now(),
    #     "qty": 1
    # })
    try:
        # the expected delivery date of territory
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer.name,
            "customer_group": eci_settings.default_customer_group,
            "transaction_date": nowdate(),
            # "eci_expected_delivery_date": expected_delivery_time,
            # "delivery_date": expected_delivery_time,
            "company": eci_settings.default_company,
            # "selling_price_list": eci_settings.default_price_list,
            "ignore_pricing_rule": 1,
            "items": items,
            # disabled discount as WooCommerce will send this both in the item rate and as discount
            #"apply_discount_on": "Net Total",
            #"discount_amount": flt(woocommerce_order.get("discount_total") or 0),
            "currency": eci_settings.default_currency,
            "is_eci_order": 1,
            "eci_shipping_territory": shipping_territory,
            "eci_shipping_address": shipping_address,
            "mode_of_payment": mode_of_payment,
            # "taxes_and_charges": tax_rules,
            # "customer_address": billing_address,
            # "shipping_address_name": shipping_address
        })
        frappe.flags.ignore_permissions = True
        frappe.set_user("administrator")
        so.insert()
        # so.submit()

        return {"message": "your_order_accepted"}
    except Exception as e:
        print(e)


@frappe.whitelist(allow_guest=False, methods=['GET'])
@eci_verify_request
def customer_orders():
    page = frappe.form_dict["page"]
    q = frappe.request.args

    if "page" in q:
        page = int(q['page']) - 1
    
    _orders = frappe.get_all("Sales Order",
                             fields=[
                                 "name", "delivery_date", "status", "total",
                                 "total_qty", "eci_shipping_cost",
                                 "eci_expected_delivery_date"
                             ],
                             filters={
                                 "customer": frappe.session.user,
                                 "is_eci_order": 1
                             },
                             order_by="name desc",
                             limit_start = page,
                             limit_page_length=20
                             )
    customer_orders = []

    for order in _orders:
        customer_orders.append({
            "id": order.name,
            "delivery_status": order.status,
            "delivery_date": order.eci_expected_delivery_date,
            "shipping": order.shipping_address,
            "status": order.status,
            "quantity": int(order.total_qty),
            "total": float(order.total),
            "shipping_total": order.eci_shipping_cost
        })
    return customer_orders

# @frappe.whitelist(allow_guest=True, methods=['POST'])
# @eci_verify_request
# def get_expected_delivery_time4():
#     # territory = frappe.form_dict["territory"]
#     # line_items = frappe.form_dict["line_items"]

#     territory = "طرابلس"
#     line_items = {"281134H000": 98}

#     warehouses = {}
#     delivery_days = []
#     all_warehouses_enough = False

#     # for each Product
#     for item in line_items:
#         # get this item warehouses
#         item_warehouses = get_item_warehouses(item)

#         _items = []

#         for itm_whs in item_warehouses:
#             # get this warehouse delivery days
#             expected_ddays = get_warehouse_delivery_days(itm_whs, territory)
#             if not expected_ddays:
#                 continue


#             _items.append({
#                 "warehouse": itm_whs,
#                 "delivery_days": expected_ddays,
#             })

#         # _items = sorted(_items, key=lambda x: x['delivery_days'], reverse=True)
#         warehouses[item] = _items

#     # # calculate the delivery days
#     iswhmax = False
#     # for prod in warehouses:


# @frappe.whitelist(allow_guest=True, methods=['POST'])
# @eci_verify_request
# def get_expected_delivery_time():
#     # territory = frappe.form_dict["territory"]
#     # line_items = frappe.form_dict["line_items"]

#     territory = "طرابلس"
#     line_items = {"281134H000": 1}

#     warehouses = {}
#     delivery_days = []
#     all_warehouses_enough = False

#     # for each Product
#     for item in line_items:
#         item_warehouses = frappe.get_all("Bin",
#                                          fields=["warehouse", "actual_qty"],
#                                          filters={"item_code": item})

#         supplier_item_warehouses = frappe.get_all("ECI Supplier Inventory",
#                                          fields=["supplier_warehouse_name as warehouse", "quantity as actual_qty"],
#                                          filters={"product": item},
#                                          order_by="modified desc")

#         if len(supplier_item_warehouses) > 0:
#             item_warehouses.append(supplier_item_warehouses[0])

#         # Get Product warehouses
#         _items = []
#         for wh in item_warehouses:
#             frappe.flags.ignore_permissions = True
#             whOrm = frappe.get_doc("Warehouse", wh.warehouse)
#             wh_delivery_dates = whOrm.expected_territory_delivery_time

#             # expected delivery days of this warehouse
#             for row in wh_delivery_dates:
#                 if row.territory == territory:
#                     _items.append({
#                         "warehouse": wh.warehouse,
#                         "required_qty": line_items[item],
#                         "actual_qty": wh.actual_qty,
#                         "delivery_days": row.expected_delivery_days,
#                         "is_enough": wh.get("actual_qty") >= line_items[item]
#                     })

#         _items = sorted(_items, key=lambda x: x['actual_qty'], reverse=True)
#         warehouses[item] = _items

#     # calculate the delivery days
#     iswhmax = False
#     for prod in warehouses:
#         for prod_wh in warehouses[prod]:
#             delivery_days.append(prod_wh.get("delivery_days"))

#             if prod_wh.get("actual_qty") >= prod_wh.get("required_qty"):
#                 all_warehouses_enough = True
#             else:
#                 iswhmax = True
#                 all_warehouses_enough = False

#     if all_warehouses_enough and not iswhmax:
#         expected_date =  add_to_date(nowdate(), days=min(delivery_days))
#         return expected_date
#     else:
#         expected_date = add_to_date(nowdate(), days=min(delivery_days))
#         return expected_date


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