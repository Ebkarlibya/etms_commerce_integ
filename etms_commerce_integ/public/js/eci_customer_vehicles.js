frappe.ui.form.on("ECI Customer Vehicles", {
    refresh: function (frm) {
        frm.set_query("vehicle_model", "customer_vehicles", function (frm, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: { "parent_compat": d.vehicle_make }
            }
        });
    }
});