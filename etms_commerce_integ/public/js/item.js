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
    }
});

frappe.ui.form.on("ECI Product Images Table", {
    refresh: function() {
        console.log('ECI Product Images Table ref');
    },
    image_title_add: function() {
        console.log('row add');
    },
    image_title: function() {
        console.log('set row');
    }
});

