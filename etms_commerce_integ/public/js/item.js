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
})