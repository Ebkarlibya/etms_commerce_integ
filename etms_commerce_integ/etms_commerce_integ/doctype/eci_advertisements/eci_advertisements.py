# Copyright (c) 2022, ebkar Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now
from frappe.model.document import Document

class ECIAdvertisements(Document):
    pass
# 	def validate(self):
#         pass


# def validate_display_schedule(self):
#     datetime_now = now()

#     for ds in self.display_schedule:
#         print(ds)
#         ads = frappe.get_all(
#                 "ECI Scheduled Advertisements",
#                 fields="*",
#                 filters={
#                     "parent": ("!=", self.name),
#                     "display_to": ("<=", ds.display_from),
#                 }
#             )
#             # where display_from < '2022-08-02 10:30:00' and display_to > '2022-08-02 15:00:00';

#         print(ads)
#         if len(ads) > 0:
#             frappe.throw(f"ECI: {frappe._(f'Display period already exist in Ad: ({ads[0].parent}')})")

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