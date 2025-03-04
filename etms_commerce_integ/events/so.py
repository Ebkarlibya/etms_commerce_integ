import frappe
# from etms_commerce_integ.notify import ets_send_notification

def on_update(doc, method):
    print("new status")
    # if doc.is_eci_order:
    #     # send notification to user via one signal
    #     ets_send_notification(
    #         message=f"تم تحديث طلبك رقم {doc.name}",
    #         username=doc.customer,
    #         data={
    #             "type": "order_status",
    #             "order_id": doc.name
    #         }
    #     )