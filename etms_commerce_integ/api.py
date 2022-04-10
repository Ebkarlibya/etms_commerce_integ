import frappe
from frappe.utils import get_url


@frappe.whitelist(allow_guest=True)
def categories():
    frappe.get_all("Item", filters={})
    categories = []
    eci_cats = frappe.get_all("ECI Category", 
        fields=["category_image", "category_name", "parent_category"])

    for cat in eci_cats:
        # count items under this category
        count = frappe.db.sql(f"""
            select count(name) from `tabECI Categories Table`
            where category_name = '{cat.category_name}' 
            or sub_category_1 = '{cat.category_name}'
        """)
        # flutter parent must be "0"
        parent = cat.parent_category
        if not cat.parent_category:
            parent = "0"
        
        # build category image url
        category_image_url = ""
        if cat.category_image:
            category_image_url = "http://192.168.1.155:8000" + cat.category_image
            #category_image_url = get_url() + cat.category_image

        categories.append({
            "id": cat.category_name,
            "name": cat.category_name,
            "slug": cat.category_name,
            "description": cat.category_description,
            "image": {"src": category_image_url},
            "parent": parent,
            "count": count[0][0]
        })
    return categories
