# Copyright (c) 2022, ebkar Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url_to_form
from frappe.utils import format_datetime
from frappe.model.document import Document

class ECIAdvertisements(Document):
    def validate(self):
        validate_display_schedule(self)

def validate_display_schedule(self):

    for ds in self.display_schedule:
        ads = frappe.get_all(
                "ECI Scheduled Advertisements",
                fields="*",
                filters={
                    "display_from": ("<", ds.display_from),
                    "display_to": (">", ds.display_from),
                }
            )

        if len(ads) > 0:            
            frappe.throw(f"""ECI: Display period already exist in:
             <a href="{get_url_to_form("ECI Advertisements", ads[0].parent)}">Ad: ({ads[0].parent})</p>
             <p>Row: {ads[0].idx}</p>
             <p>From: {format_datetime(ads[0].display_from, "yyyy-mm-dd HH:mm")}</p>
             <p>To: {format_datetime(ads[0].display_to, "yyyy-mm-dd HH:mm")}</p>
             """)

# def is_ad_exist(self):
# 	ads = frappe.get_all(
# 		"ECI Advertisements",
# 		fields=["display_order"],
# 		filters={
# 			"name": ("!=", self.name),
# 			"display_order": self.display_order
# 		}
# 	)
# 	if len(ads) > 0:
# 		frappe.throw(f"ECI: {frappe._(f'Another Ad with display order: {self.display_order} already exists')}")