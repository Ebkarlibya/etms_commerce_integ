frappe.ui.form.on("Item", {
    refresh: function (frm) {
        frm.set_query("category_name", "eci_categories", function (frm) {
            return {
                filters: { "parent_eci_category": "" }
            }
        });
        frm.set_query("sub_category_1", "eci_categories", function (frm, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: { "parent_eci_category": d.category_name }
            }
        });
        frm.set_query("vehicle_model", "eci_vehicle_compatibility", function (frm, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: { "parent_compat": d.vehicle_make }
            }
        });

        // items insert dialog
        // let compat_table = document.querySelector("div[data-fieldname='eci_vehicle_compatibility']");
        // compat_table.style.maxHeight = "800px";
        // compat_table.style.overflowY = "auto";
        let eci_cb1 = frm.get_field("eci_vehicle_compatibility").grid.add_custom_button(frappe._("ECI Bulk Insert"), function () {
            let d = new frappe.ui.Dialog({
                title: frappe._('ECI Bulk Insert'),
                fields: [{
                    label: frappe._('Vehicle Make'),
                    fieldname: 'vehicle_make',
                    fieldtype: 'Link',
                    options: "ECI Vehicle Make",
                    change: function (e) {
                        let self = d.get_field("vehicle_make");
                        let model = d.get_field("vehicle_model");
                        if (!self.value) {
                            model.df.read_only = true;
                        } else {
                            model.df.read_only = false;
                        }
                        model.refresh();
                    }
                }, {

                    fieldname: 'column_break0',
                    fieldtype: 'Column Break',
                }, {
                    label: frappe._('Vehicle Model'),
                    fieldname: 'vehicle_model',
                    fieldtype: 'Link',
                    options: "ECI Vehicle Model",
                    get_query: function (frm) {
                        return {
                            filters: {
                                parent_compat: d.get_value("vehicle_make")
                            }
                        }

                    }
                }, {
                    label: frappe._("Year Range"),
                    fieldname: 'section_break1',
                    fieldtype: 'Section Break',
                }, {
                    label: frappe._('Year From'),
                    fieldname: 'year_from',
                    fieldtype: 'Link',
                    options: 'ECI Vehicle Year',
                    change: function (e) {
                        let self = d.get_field("year_from");
                        let year_to = d.get_field("year_to");
                        if (!self.value) {
                            year_to.df.read_only = true;
                        } else {
                            year_to.df.read_only = false;
                        }
                        year_to.refresh();
                    }
                }, {
                    fieldname: 'col_break1',
                    fieldtype: 'Column Break'
                }, {
                    label: frappe._('Year To'),
                    fieldname: 'year_to',
                    fieldtype: 'Link',
                    options: 'ECI Vehicle Year',
                    get_query: function (frm) {
                        let year_from = d.get_value("year_from");

                        return {
                            filters: [['year', '>', year_from]]

                        }
                    }
                },
                {
                    fieldname: 'sec_break2',
                    fieldtype: 'Section Break'
                }, {
                    label: frappe._('Note'),
                    fieldname: 'compat_note',
                    fieldtype: 'Small Text'
                }],
                primary_action_label: frappe._('Insert Vehicles'),
                primary_action(values) {

                    for (var start = values.year_from; start <= values.year_to; start++) {
                        var r = frm.add_child('eci_vehicle_compatibility');
                        r.vehicle_make = values.vehicle_make;
                        r.vehicle_model = values.vehicle_model;
                        r.vehicle_year = start;
                        r.compat_note = values.compat_note;
                    }
                    refresh_field("eci_vehicle_compatibility");
                    d.hide();
                }
            });
            d.show();
            d.get_field("vehicle_model").df.read_only = true;
            d.get_field("vehicle_model").refresh();
            d.get_field("year_to").df.read_only = true;
            d.get_field("year_to").refresh();
        }, 2);
        eci_cb1.css("background-color", "var(--gray-100)");
        eci_cb1.css("margin-right", "5px");
        eci_cb1.css("margin-left", "5px");

        // add eci supplier stock levels dashboard
        if(cur_frm.doc.item_code) {
            frappe.call({
                method: "etms_commerce_integ.utils.get_item_stock_levels",
                args: {
                    item_code: frm.doc.item_code
                },
                callback: function (r) {
                    if(r.message == undefined || r.message.length == 0) return;
                    let html = "";
                    
                    for (let entry of r.message) {
                        html += `
                                <div class="dashboard-list-item">
                                <div class="row">
                                    <div class="col-sm-3" style="margin-top: 8px;">
                                        <a data-type="warehouse" data-name="${entry.warehouse}">${entry.warehouse}</a>
                                    </div>
                                    <div class="col-sm-3" style="margin-top: 8px;">
                                        
                                            <a data-type="item"
                                                data-name="${frm.doc.item_code}">${frm.doc.item_code} (${frm.doc.item_name})
                                            </a>
                                    </div>
                                    <div class="col-sm-4" style="margin-top: 8px;">
                                        <span class="inline-graph">
                                            <span>
                                                ${entry.quantity} (Qty)
                                            </span>
                                        </span>
                                    </div>
                
                                    <div class="col-sm-2 text-right" style="margin: var(--margin-sm) 0;">
            
                                        <button style="margin-left: 7px;" class="btn btn-default btn-xs btn-add"
                                            onclick="frappe.new_doc('ECI Supplier Inventory', {'product': '${frm.doc.item_code}'})">${frappe._("Add")}</a>
                                    </div>
            
                                </div>
                            </div>
                        `
                    }
                    frm.dashboard.add_section(html, frappe._("ECI Multi Vendor Stock Levels"));
                }
            });
        }
    }
});

frappe.ui.form.on("Item", {
    before_save: function (frm) {
        if(frm.doc.warehouses_to_check_item_availability) {
            const mappedList = frm.doc.warehouses_to_check_item_availability.map(i => i.warehouse);
    
            if (new Set(mappedList).size !== mappedList.length) {
                frappe.throw(frappe._("ECI: Duplicated warehouses not allowed."));
            }
        }
    }
})

// frappe.ui.form.on("ECI Product Images Table", {
//     refresh: function () {
//         console.log('ECI Product Images Table ref');
//     },
//     image_title_add: function () {
//         console.log('row added');
//     },
//     product_image: function (frm, cdt, cdn) {
//         let d = locals[cdt, cdn];
//         d.item_title = frm.doc.image_title;
//     }
// });


frappe.ui.form.on("ECI Supplier Warehouse Table", {
    supplier_warehouse: function (frm, cdt, cdn) {
        var row = frappe.get_doc(cdt, cdn)
        frappe.db.get_value("ECI Supplier Warehouse", { name: row.supplier_warehouse }, "supplier_name").then(function (r) {
            row.supplier_name = r.message.supplier_name;
            frm.refresh_fields()
        })
    }
})
