import frappe

@frappe.whitelist(allow_guest=False)
def update_user_profile(first_name, last_name, shipping_address_1, shipping_city, shipping_country):
# "{"first_name":"imad","last_name":"abdou","shipping_address_1":"tripoli near ....",
# "shipping_city":"tripoli","shipping_country":"ليبيا"}"

    frappe.only_for("Customer")
    
    user = frappe.get_doc("User", frappe.session.user)

    user.first_name = first_name 
    user.last_name = last_name

    user.save()
    address = None
    if len(frappe.get_all("Address", filters={"name": f"{user.name}-Shipping"})) == 0:
        new_address = frappe.get_doc({
            "doctype": "Address",
            "address_title": user.name,
            "address_type": "Shipping",
            "address_line1": shipping_address_1,
            "city": shipping_city,
            "country": "Libya",
            "email_id": user.email,
            "phone": user.mobile_no
        })
        new_address.insert()
    else:
        address = frappe.get_doc("Address", f"{user.name}-Shipping")
        address.address_line1 = shipping_address_1
        address.city = shipping_city
        address.country = "Libya"
        address.flags.ignore_mandatory = True
        address.save()
    return {
        "id": user.name,
        "displayname": user.full_name,
        "name": user.name,
        "username": user.name,
        "firstname": user.first_name,
        "lastname": user.last_name,
        "email": user.email,
        "nicename": user.full_name,
        "url": "USER URL...",
        "roles": [],
        "address_line1": address.address_line1,
        "city": address.city,
        "message": "profile_updated"
    }

    #       id = json['id'].toString();
    #   name = json['displayname'];
    #   username = json['username'];
    #   firstName = json['firstname'];
    #   lastName = json['lastname'];
    #   email = json['email'];
    #   picture = json['avatar'];
    #   nicename = json['nicename'];
    #   userUrl = json['url'];
    #   loggedIn = true;
    #   var roles = json['roles'] as List;