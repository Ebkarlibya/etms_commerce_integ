frappe.ui.form.on("Item", {
    refresh: function(frm) {
        frm.set_query("category_name", "eci_categories", function(frm) {
            return {
                filters: {"parent_eci_category": ""}
            }
        });
        frm.set_query("sub_category_1", "eci_categories", function(frm, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {"parent_eci_category": d.category_name}
            }
        });
        frm.set_query("vehicle_model", "eci_vehicle_compatibility", function(frm, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {"parent_compat": d.vehicle_make}
            }
        });
    }
});

frappe.ui.form.on("Item", {
    before_save: function(frm) {
        const mappedList = frm.doc.warehouses_to_check_item_availability.map(i=>i.warehouse);
        
        if( new Set(mappedList).size !== mappedList.length ) {
            frappe.throw(frappe._("ECI: Duplicated warehouses not allowed."));
        }
    }
})

frappe.ui.form.on("ECI Product Images Table", {
    refresh: function() {
        console.log('ECI Product Images Table ref');
    },
    image_title_add: function() {
        console.log('row added');
    },
    product_image: function(frm, cdt, cdn) {
        let d = locals[cdt, cdn];
        d.item_title = frm.doc.image_title;
    }
});

