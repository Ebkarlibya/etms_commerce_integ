import frappe
from frappe.utils import get_url
from frappe.desk.treeview import get_children

@frappe.whitelist(allow_guest=True)
def categories():
    frappe.get_all("Item", filters={})
    categories = []
    eci_cats = frappe.get_all("ECI Category",
        fields=["category_image", "category_name", "parent_eci_category"])

    for cat in eci_cats:
        # count items under this category
        count = frappe.db.sql(f"""
            select count(name) from `tabECI Categories Table`
            where category_name = '{cat.category_name}' 
            or sub_category_1 = '{cat.category_name}'
        """)
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
            "count": count[0][0]
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
    prod_filters = {}
    products_list = []

    if "id" in query_params:
        prod_filters["item_code"] = query_params["id"]
    eci_products = frappe.get_all("Item",
        fields=["item_code", "item_name", "description"],
        filters=prod_filters)

    for prod in eci_products:
        # get product price
        price = frappe.get_all("Item Price",
            fields=["price_list_rate"],
            filters={"item_code": prod.item_code},
            order_by="valid_from desc")[0]["price_list_rate"]
        # is the product available in stock
        actual_qty = frappe.get_all("Bin",
            fields=["actual_qty"],
            filters={"item_code": prod.item_code
        })[0]["actual_qty"]
        inStock = True if actual_qty >= 1 else False

        # get product categories
        product_categories = frappe.get_all("ECI Categories Table",
                              fields=["category_name", "sub_category_1"],
                              filters={"parent": prod.item_code})
        # get product images
        product_images = frappe.get_all("ECI Product Images Table",
                                        fields=["product_image", "image_title"],
                                        filters={"parent": prod.item_code})
        # product_image_url = "http://192.168.1.155:8000" + prod.category_image
        #category_image_url = get_url() + cat.category_image

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
            # cat props id, name, slug
            "categories": [
                {"id": "0", "name": c.sub_category_1 or c.category_name, "slug": "asd"}
                for c in product_categories],
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