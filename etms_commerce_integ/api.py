import frappe
from frappe.utils import get_url
from frappe.desk.treeview import get_children
from urllib.parse import unquote
from etms_commerce_integ.auth import eci_verify_request
from etms_commerce_integ.utils import eci_log_error, get_item_price


@frappe.whitelist(allow_guest=False)
@eci_verify_request
def upload_file():
    files = frappe.request.files
    is_private = False  #frappe.form_dict.is_private
    doctype = "ECI Parts Request"  #frappe.form_dict.doctype
    docname = frappe.form_dict.request_name  #frappe.form_dict.docname
    fieldname = ""  #frappe.form_dict.fieldname
    file_url = ""  #frappe.form_dict.file_url
    folder = "Home"  #frappe.form_dict.folder or 'Home'
    filename = frappe.form_dict.file_name
    content = None

    if 'file' in files:
        file = files['file']
        content = file.stream.read()
        filename = file.filename

    frappe.local.uploaded_file = content
    frappe.local.uploaded_filename = filename

    import mimetypes
    filetype = mimetypes.guess_type(filename)[0]
    if filetype not in ('image/png', 'image/jpeg'):
        return {"message": "file_format_not_allowed"}

    ret = frappe.get_doc({
        "doctype": "File",
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "attached_to_field": fieldname,
        "folder": folder,
        "file_name": filename,
        "file_url": file_url,
        "is_private": is_private,
        "content": content
    })
    ret.save(ignore_permissions=True)
    return {"message": "file_uploaded_successfully"}


@frappe.whitelist(allow_guest=False, methods=["POST"])
@eci_verify_request
def request_part():
    part_make = frappe.form_dict["part_make"]
    part_model = frappe.form_dict["part_model"]
    part_year = frappe.form_dict["part_year"]
    part_status = frappe.form_dict["part_status"]
    part_description = frappe.form_dict["part_description"]

    if part_status == '1':
        part_status = "New"
    elif part_status == '2':
        part_status = "Used"
    elif part_status == '3':
        part_status = "Any"

    part_request = frappe.get_doc({
        "doctype": "ECI Parts Request",
        "part_make": part_make,
        "part_model": part_model,
        "part_year": part_year,
        "part_status": part_status,
        "part_description": part_description,
        "requested_by": frappe.session.user
    })
    part_request.flags.ignore_permissions = True
    part_request.insert()
    # request_rejected
    return {"message": "request_accepted", "request_name": part_request.name}


@frappe.whitelist(allow_guest=True)
@eci_verify_request
def categories():
    frappe.get_all("Item", filters={})
    categories = []
    eci_settings = frappe.get_single("ECI Commerce Settings")

    eci_categories = frappe.get_all(
        "ECI Category",
        fields=["category_image", "category_name", "parent_eci_category"],
        order_by="order_weight asc")

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
            category_image_url = eci_settings.eci_domain + cat.category_image
            #category_image_url = get_url() + cat.category_image

        categories.append({
            "id": cat.category_name,
            "name": cat.category_name,
            "slug": cat.category_name,
            "description": cat.category_description,
            "image": {
                "src": category_image_url
            },
            "parent": parent,
            "count": 0
        })
    return categories


@frappe.whitelist(allow_guest=True, methods=["GET"])
@eci_verify_request
def products():
    try:
        q = frappe.request.args
        eci_settings = frappe.get_single("ECI Commerce Settings")
        
        page = 0
        per_page = 20

        if "page" in q:
            page = int(q['page']) - 1
        offset = page * per_page

        sql_escaped_values = {}
        sql_id_cond = ""
        sql_term_cond = ""
        sql_brand_cond = ""
        sql_product_condition_cond = ""
        sql_is_inspected_cond = ""
        sql_has_warranty_cond = ""
        sql_cat_cond = ""
        sql_tag_cond = ""
        sql_comp_cond = ""

        products_list = []

        # get product by id
        if "id" in q:
            sql_escaped_values["id"] = q["id"]
            sql_id_cond = """
                and i.item_code = %(id)s
            """

        # search box
        if "search" in q:
            sql_escaped_values["search"] = f"%{q['search']}%"
            sql_escaped_values["tagterm"] = f"{q['search']}"

            sql_term_cond = """
                and (
                    i.item_name like %(search)s
                    or i.description like %(search)s
                    or %(tagterm)s in (
                        select tag_name from `tabECI Product Tags Table`
                        where parent = i.item_code
                        and tag_name = %(tagterm)s
                    )
                )
            """

        # Extra filters
        if "brand" in q and q["brand"]:
            sql_escaped_values["brand"] = f"{q['brand']}"
            sql_brand_cond = """
                and i.brand = %(brand)s
            """

        if "productCondition" in q and q["productCondition"]:
            if q["productCondition"] == "جديد":
                sql_product_condition_cond = """
                    and i.eci_product_condition = "New"
                """
            elif q["productCondition"] == "مستعمل":
                sql_product_condition_cond = """
                    and i.eci_product_condition = "Used"
                """
        
        if "is_inspected" in q and q["is_inspected"]:

            if q["is_inspected"] == "مع فحص الجودة":
                sql_is_inspected_cond = """
                    and i.is_inspected = "Yes"
                """
            elif q["is_inspected"] == "بدون فحص الجودة":
                sql_is_inspected_cond = """
                    and i.is_inspected = "No"
                """

        if "has_warranty" in q and q["has_warranty"]:

            if q["has_warranty"] == "مع ضمان":
                sql_has_warranty_cond = """
                    and i.has_warranty = "Yes"
                """
            if q["has_warranty"] == "بدون ضمان":
                sql_has_warranty_cond = """
                    and i.has_warranty = "No"
                """


        # category search
        if "category" in q:
            sql_escaped_values["category"] = q["category"]
            sql_cat_cond = """
                and exists(
                    select c.category_name, c.sub_category_1, c.parent
                    from `tabECI Categories Table` c
                    where (c.category_name = %(category)s or c.sub_category_1 = %(category)s)
                    and i.item_code = c.parent
                )
            """
        
        # tags search
        if "tag" in q:
            sql_escaped_values["tag"] = q["tag"]
            sql_tag_cond = """
                and exists (
                    select tag_name from `tabECI Product Tags Table`
                    where parent = i.item_code
                    and tag_name = %(tag)s
                )
            """

        if "veh-compat-make" in q:
            sql_escaped_values["veh-compat-make"] = q["veh-compat-make"]
            sql_escaped_values["veh-compat-model"] = q["veh-compat-model"]
            sql_escaped_values["veh-compat-year"] = q["veh-compat-year"]
            sql_comp_cond = """
                and exists (
                    select v.vehicle_make, v.vehicle_model, v.vehicle_year, v.parent 
                    from `tabECI Vehicle Compatibility Table` v
                    where v.vehicle_make = %(veh-compat-make)s
                    and v.vehicle_model = %(veh-compat-model)s
                    and v.vehicle_year = %(veh-compat-year)s
                    and i.item_code = v.parent
            )
            """

        eci_products = frappe.db.sql(f"""
            select i.item_name, i.item_code, i.brand, i.description, i.eci_product_condition,
            i.has_specific_compatibility, i.standard_rate, i.is_inspected, i.inspection_note,
            i.has_warranty, i.warranty_note, sum(b.actual_qty) prod_total_whs_qty

            from `tabItem` i
            inner join `tabBin` b
            on i.item_code = b.item_code
            where i.publish_to_commerce_app = 1
            {sql_id_cond}
            {sql_cat_cond}
            {sql_comp_cond}
            {sql_brand_cond}
            {sql_product_condition_cond}
            {sql_is_inspected_cond}
            {sql_has_warranty_cond}
            {sql_term_cond}
            {sql_tag_cond}

            group by i.item_code
            order by i.creation
            limit {offset},{per_page}
        """, sql_escaped_values, as_dict=True, debug=False)


        for prod in eci_products:
            # if product not in publish warehouses skip
            # filtered using sql
            # product_warehouses = frappe.db.sql(f"""
            #     select warehouse, actual_qty
            #     from `tabBin` where item_code = '{prod.item_code}'
            #     and warehouse in (
            #         select warehouse
            #         from `tabECI Publish Warehouses Table`
            #         where parent='{prod.item_code}'
            #         )
            #     """,
            #     as_dict=True)

            # Get product price
            price = get_item_price(prod.item_code)


            # Is the product available in stock
            # actual_qty = 0
            # for item in product_warehouses:
            #     actual_qty += item[
            #         "actual_qty"]  # sum qty in all eci published warehouses
            inStock = True if prod.prod_total_whs_qty >= 1 else False

            # Get product categories
            product_categories = []
            _product_categories = frappe.get_all(
                "ECI Categories Table",
                fields=["category_name", "sub_category_1"],
                filters={"parent": prod.item_code})

            for prod_cat in _product_categories:
                if prod_cat.category_name:
                    product_categories.append({
                        "id": prod_cat.category_name,
                        "name": prod_cat.category_name,
                        "slug": prod_cat.category_name
                    })
                if prod_cat.sub_category_1:
                    product_categories.append({
                        "id": prod_cat.sub_category_1,
                        "name": prod_cat.sub_category_1,
                        "slug": prod_cat.sub_category_1
                    })
            # Get product tags
            product_tags = []
            _product_tags = frappe.get_all(
                "ECI Product Tags Table",
                fields=["name", "tag_name"],
                filters={"parent": prod.item_code})

            for tag in _product_tags:
                product_tags.append(
                    {
                        "id": tag.name, 
                        "name": tag.tag_name,
                        "slug": "-".join(tag.tag_name.split(' '))
                    }
                )

            # Get product images
            product_images = []
            _product_images = frappe.get_all(
                "ECI Product Images Table",
                fields=["product_image", "image_title"],
                filters={"parent": prod.item_code},
                order_by="idx asc")

            for pImage in _product_images:
                if pImage.product_image:
                    product_images.append(
                        {
                            "src": eci_settings.eci_domain + pImage.product_image,
                            "name": pImage.product_image,
                            # "alt": "",
                            # "position": 0
                        } 
                    )

            # Get product vehicle compatibility
            vehicleCompatsList = []
            if prod.has_specific_compatibility == 1:
                vehicleCompatsList = frappe.db.sql(f"""
                    select vehicle_make, vehicle_model, vehicle_year,
                    compat_note
                    from `tabECI Vehicle Compatibility Table`
                    where parent='{prod.item_code}'
                    order by idx asc
                    """,
                    as_dict=True)

            products_list.append({
                "id": prod.item_code,
                "name": prod.item_name,
                "slug": prod.item_name,
                "type":
                "simple",
                "status":
                "publish",
                "featured": False,
                #"catalog_visibility": "visible",
                "brand": prod.brand,
                "description": prod.description,
                #"short_description": prod.description,
                #"sku": "asd-dsa-dsa",
                "price": price,
                #"regular_price": 25, show up as discounted price in flutter
                "sale_price": price,
                #"stock_quantity": 70,
                "in_stock": inStock,
                "isInspected": prod.is_inspected,
                "inspectionNote": prod.inspection_note,
                "hasWarranty": prod.has_warranty,
                "warrantyNote": prod.warranty_note,
                "productCondition": "0" if prod.eci_product_condition == "New" else "1",
                "categories": product_categories,
                "vehicleCompatsList": vehicleCompatsList,
                "tags": product_tags,
                "images": product_images,
                "variations": [],
                "attributes": [{
                    "id": 3,
                    "name": "car-makes",
                    "position": 0,
                    "visible": True,
                    "variation": False,
                    "options": ["Hyundai"]
                }, {
                    "id":2,
                    "name":
                    "car-model",
                    "position": 1,
                    "visible": False,
                    "variation": False,
                    "options": ["hyundai avante 2005 2006 2007 2008 2009"]
                }],
                "meta_data": [{
                    "id": 22120,
                    "key": "recommend_product",
                    "value": "0"
                }, {
                    "id": 22259,
                    "key": "condition",
                    "value": "New"
                }, {
                    "id": 22260,
                    "key": "_condition",
                    "value": "field_601e5462ad58a"
                }, {
                    "id": 22261,
                    "key": "rs_page_bg_color",
                    "value": ""
                }, {
                    "id": 22262,
                    "key": "page_header_hide",
                    "value": "0"
                }, {
                    "id": 22263,
                    "key": "page_header_style",
                    "value": ""
                }, {
                    "id": 22264,
                    "key": "page_footer_hide",
                    "value": "0"
                }, {
                    "id": 22265,
                    "key": "page_footer_style",
                    "value": ""
                }, {
                    "id": 22266,
                    "key": "copyright_footer_style",
                    "value": ""
                }, {
                    "id": 22267,
                    "key": "page_sidebar_layout",
                    "value": ""
                }, {
                    "id": 22268,
                    "key": "page_sidebar_template",
                    "value": ""
                }, {
                    "id": 22269,
                    "key": "featured_video_product",
                    "value": ""
                }, {
                    "id": 22270,
                    "key": "newproduct",
                    "value": "0"
                }, {
                    "id": 22275,
                    "key": "post_views_count",
                    "value": "94"
                }, {
                    "id": 22307,
                    "key": "_yoast_wpseo_primary_vehicle-info",
                    "value": "670"
                }, {
                    "id": 22463,
                    "key": "is_compatible_with_all_vehicles",
                    "value": "Compatible With Specific Vehicles"
                }, {
                    "id": 22464,
                    "key": "_is_compatible_with_all_vehicles",
                    "value": "field_61348a84db811"
                }]
            })
        return products_list
    except Exception as e:
        eci_log_error()
        print(e)
        return []
