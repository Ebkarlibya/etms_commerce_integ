frappe.ui.form.on("ECI Advertisements", {
    refresh: function (frm) {
        frm.set_query("vehicle_model", "to_customer_vehicles", function (frm, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: { "parent_compat": d.vehicle_make }
            }
        });
    }
});