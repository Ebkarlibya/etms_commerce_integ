import frappe
from frappe.utils import get_url
from frappe.desk.treeview import get_children
from urllib.parse import unquote

@frappe.whitelist(allow_guest=True)
def categories():
    frappe.get_all("Item", filters={})
    categories = []
    eci_categories = frappe.get_all("ECI Category",
        fields=["category_image", "category_name", "parent_eci_category"])

    for cat in eci_categories:
        # count items under this category
        # count = frappe.db.sql(f"""
        #     select count(name) from `tabECI Categories Table`
        #     where category_name = '{cat.category_name}' 
        #     or sub_category_1 = '{cat.category_name}'
        # """)
        # flutter parent must be "0"
        parent = cat.parent_eci_category
        if not cat.parent_eci_category:
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
            "count": 0
        })
    return categories

@frappe.whitelist(allow_guest=True)
def products():
    # extract query params
    query_params = dict(
        q.split("=")
        for q in frappe.request.query_string.decode("utf-8").split("&")
    )

    # get related product/s
    products_list = []
    eci_products = []
    # filters
    if "id" in query_params:
        eci_products = frappe.db.sql(f"""
            select i.item_name, i.item_code, i.description, i.eci_is_product_used,
            i.has_specific_compatibility
            from `tabItem` i
            where i.publish_to_commerce_app = 1
            and i.item_code = '{query_params['id']}'
            ;
        """, as_dict=True)
    elif "category" in query_params:
        decoded_cat = unquote(query_params["category"])
        eci_products = frappe.db.sql(f"""
            select i.item_name, i.item_code, i.description, i.eci_is_product_used,
            i.has_specific_compatibility, c.category_name,c.sub_category_1
            from `tabItem` i inner join `tabECI Categories Table` c
            ON i.item_code = c.parent
            where i.publish_to_commerce_app = 1
            and c.category_name='{decoded_cat}' or c.sub_category_1='{decoded_cat}';
            ;
        """, as_dict=True)
    else:
        eci_products = frappe.db.sql(f"""
            select i.item_name, i.item_code, i.description, i.eci_is_product_used,
            i.has_specific_compatibility
            from `tabItem` i
            where i.publish_to_commerce_app = 1
            ;
        """, as_dict=True)

    for prod in eci_products:
        # if product not in publish warehouses skip
        product_warehouses = frappe.db.sql(f"""
            select warehouse, actual_qty
            from `tabBin` where item_code = '{prod.item_code}'
            and warehouse in (
                select warehouse
                from `tabECI Publish Warehouses Table`
                where parent='{prod.item_code}'
                )
            """, as_dict=True)
        # if len(product_warehouses) < 1:
        #     continue

        # get product price
        price = frappe.get_all("Item Price",
            fields=["price_list_rate"],
            filters={"price_list": prod.commerce_app_price_list or "Standard Selling", "item_code": prod.item_code},
            order_by="valid_from desc")[0]["price_list_rate"]

        # is the product available in stock
        actual_qty = 0
        for item in product_warehouses:
            actual_qty += item["actual_qty"] # sum qty in all eci published warehouses
        inStock = True if actual_qty >= 1 else False

        # get product categories
        _product_categories = frappe.get_all("ECI Categories Table",
                              fields=["category_name", "sub_category_1"],
                              filters={"parent": prod.item_code})

        product_categories = []
        for prod_cat in _product_categories:
            if prod_cat.category_name:
                product_categories.append(
                    {"id": prod_cat.category_name, "name": prod_cat.category_name, "slug": prod_cat.category_name}
                )
            if prod_cat.sub_category_1:
                product_categories.append(
                    {"id": prod_cat.sub_category_1, "name": prod_cat.sub_category_1, "slug": prod_cat.sub_category_1}
                )

        # get product images
        product_images = frappe.get_all("ECI Product Images Table",
                                        fields=["product_image", "image_title"],
                                        filters={"parent": prod.item_code})
        # product_image_url = "http://192.168.1.155:8000" + prod.category_image
        #category_image_url = get_url() + cat.category_image

        # get product vehicle compatibility
        vehicleCompatsList = []
        if prod.has_specific_compatibility == 1:
            vehicleCompatsList = frappe.db.sql(f"""
                select vehicle_make, vehicle_model, vehicle_year
                from `tabECI Vehicle Compatibility Table`
                where parent='{prod.item_code}';
                """, as_dict=True)
        print(prod.eci_is_product_used)
        products_list.append({
            "id": prod.item_code,
            "name": prod.item_name,
            "slug": prod.item_name,
            "type": "simple",
            "status": "publish",
            "featured": False,
            #"catalog_visibility": "visible",
            "description": prod.description,
            #"short_description": prod.description,
            #"sku": "asd-dsa-dsa",
            "price": price,
            #"regular_price": 25, show up as discounted price in flutter
            "sale_price": price,
            #"stock_quantity": 70,
            "in_stock": inStock,
            "condition": str(prod.eci_is_product_used),
            "categories": product_categories,
            "vehicleCompatsList": vehicleCompatsList,
            "tags": [
                # {
                #     "id": 664,
                #     "name": "فلتر زيت افانتي",
                #     "slug": "falatir-zait-avanti"
                # }
            ],
            "images": [
                {
                    # "id": 7154,
                    # "date_created": "2021-08-17T12:45:22",
                    # "date_created_gmt": "2021-08-17T12:45:22",
                    # "date_modified": "2021-08-17T12:45:22",
                    # "date_modified_gmt": "2021-08-17T12:45:22",
                    "src": "http://192.168.1.155:8000" + pi.product_image,
                    "name": pi.product_image,
                    # "alt": "",
                    # "position": 0
                }
                for pi in product_images 
            ],
            "variations": [],
            "attributes": [
                {
                    "id": 3,
                    "name": "car-makes",
                    "position": 0,
                    "visible": True,
                    "variation": False,
                    "options": [
                    "Hyundai"
                    ]
                },
                {
                    "id": 2,
                    "name": "car-model",
                    "position": 1,
                    "visible": False,
                    "variation": False,
                    "options": [
                        "hyundai avante 2005 2006 2007 2008 2009"
                    ]
                }
            ],
            "meta_data": [
                {
                    "id": 22120,
                    "key": "recommend_product",
                    "value": "0"
                },
                {
                    "id": 22259,
                    "key": "condition",
                    "value": "New"
                },
                {
                    "id": 22260,
                    "key": "_condition",
                    "value": "field_601e5462ad58a"
                },
                {
                    "id": 22261,
                    "key": "rs_page_bg_color",
                    "value": ""
                },
                {
                    "id": 22262,
                    "key": "page_header_hide",
                    "value": "0"
                },
                {
                    "id": 22263,
                    "key": "page_header_style",
                    "value": ""
                },
                {
                    "id": 22264,
                    "key": "page_footer_hide",
                    "value": "0"
                },
                {
                    "id": 22265,
                    "key": "page_footer_style",
                    "value": ""
                },
                {
                    "id": 22266,
                    "key": "copyright_footer_style",
                    "value": ""
                },
                {
                    "id": 22267,
                    "key": "page_sidebar_layout",
                    "value": ""
                },
                {
                    "id": 22268,
                    "key": "page_sidebar_template",
                    "value": ""
                },
                {
                    "id": 22269,
                    "key": "featured_video_product",
                    "value": ""
                },
                {
                    "id": 22270,
                    "key": "newproduct",
                    "value": "0"
                },
                {
                    "id": 22275,
                    "key": "post_views_count",
                    "value": "94"
                },
                {
                    "id": 22307,
                    "key": "_yoast_wpseo_primary_vehicle-info",
                    "value": "670"
                },
                {
                    "id": 22463,
                    "key": "is_compatible_with_all_vehicles",
                    "value": "Compatible With Specific Vehicles"
                },
                {
                    "id": 22464,
                    "key": "_is_compatible_with_all_vehicles",
                    "value": "field_61348a84db811"
                }
                ]
        })
    return products_list