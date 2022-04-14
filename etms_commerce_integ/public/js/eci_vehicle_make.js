frappe.ui.form.on("ECI Vehicle Make", {
    refresh: function(frm) {
        var parent_compat = frm.doc.make;
        if(!frm.doc.__unsaved == 1) {
            frm.add_custom_button("Create Model Compat", function() {
                frappe.new_doc("ECI Vehicle Model", {parent_compat: parent_compat});
            })
        }
    }
});