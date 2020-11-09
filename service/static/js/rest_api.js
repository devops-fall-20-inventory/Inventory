$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        console.log(res);
        $("#inventory_product_id").val(res.product_id);
        $("#inventory_quantity").val(res.quantity);
        $("#inventory_restock_level").val(res.restock_level);
        if (res.available == 1) {
            $("#inventory_available").val("true");
        } else {
            $("#inventory_available").val("false");
        }
        if (res.condition == "new") {
            $("#inventory_condition").val("new");
        } else if (res.condition == "used") {
            $("#inventory_condition").val("used");
        } else {
            $("#inventory_condition").val("open-box");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#inventory_product_id").val("");
        $("#inventory_condition").val("");
        $("#inventory_quantity").val("");
        $("#inventory_restock_level").val("");
        $("#inventory_available").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Inventory
    // ****************************************

    $("#create-btn").click(function () {

        var pid = $("#inventory_product_id").val();
        var qty = $("#inventory_quantity").val();
        var lvl = $("#inventory_restock_level").val();
        var cnd_val = $("#inventory_condition").val();
        var cnd = "new";
        if (cnd_val == "used")
            cnd = "used"
        else if (cnd_val == "open-box")
            cnd = "open box";
        var avl_val = $("#inventory_available").val("");
        var avl = 1;
        if (avl_val == "false")
            avl = 0;

        var data = {
            "product_id": parseInt(pid),
            "condition": cnd,
            "quantity": parseInt(qty),
            "restock_level": parseInt(lvl),
            "available": avl
        };

        if (pid && cnd && qty && lvl && avl) {
            var ajax = $.ajax({
                type: "POST",
                url: "/inventory",
                contentType: "application/json",
                data: JSON.stringify(data),
            });
            ajax.done(function(res) {
                update_form_data(res);
                flash_message("Success");
            });
            ajax.fail(function(res) {
                flash_message(res.responseJSON.message);
            });
        }
        else {
            var msg = "All fields are necessary.\nProduct ID>0, Quantity>=0, Restock level>=0";
            flash_message(msg);
        }
    });

    // ****************************************
    // Update a Inventory
    // ****************************************

    $("#update-btn").click(function () {

        var pid = $("#inventory_product_id").val();
        var qty = $("#inventory_quantity").val();
        var lvl = $("#inventory_restock_level").val();
        var cnd_val = $("#inventory_condition").val();
        var cnd = "new";
        if (cnd_val == "used")
            cnd = "used"
        else if (cnd_val == "open-box")
            cnd = "open box";
        var avl_val = $("#inventory_available").val("");
        var avl = 1;
        if (avl_val == "false")
            avl = 0;

        var data = {
            "quantity": parseInt(qty),
            "restock_level": parseInt(lvl),
            "available": avl
        };

        if (pid && cnd) {
            var ajax = $.ajax({
                type: "PUT",
                url: "/inventory/" + pid + "/condition/" + cnd,
                contentType: "application/json",
                data: JSON.stringify(data)
            });
            ajax.done(function(res){
                update_form_data(res)
                flash_message("Success")
            });
            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });
        }
        else {
            flash_message('Product ID AND Condition is required')
        }
    });

    // ****************************************
    // Retrieve an Inventory
    // ****************************************

    $("#retrieve-btn").click(function () {

        var pid = $("#inventory_product_id").val();
        var cnd_val = $("#inventory_condition").val();
        var cnd = "new";
        if (cnd_val == "used")
            cnd = "used"
        else if (cnd_val == "open-box")
            cnd = "open box";
        if (pid && cnd) {
            var ajax = $.ajax({
                type: "GET",
                url: "/inventory/" + pid + "/condition/" + cnd,
                contentType: "application/json",
                data: ''
            })
            ajax.done(function(res) {
                update_form_data(res)
                flash_message("Success")
            });
            ajax.fail(function(res){
                clear_form_data()
                flash_message(res.responseJSON.message)
            });
        }
        else {
            flash_message('Product ID AND Condition is required')
        }
    });

    // ****************************************
    // Search for a collection of Inventories
    // ****************************************

    /*$("#search-btn").click(function () {

        var pid = $("#inventory_product_id").val();
        var qty = $("#inventory_quantity").val();
        var cnd_val = $("#inventory_condition").val();
        var cnd = "new";
        if (cnd_val == "used")
            cnd = "used"
        else if (cnd_val == "open-box")
            cnd = "open box";

        var queryString = "";
        if (pid) {
            queryString += 'product_id=' + name
        }
        if (qty) {
            queryString += 'quantity=' + qty;
            if (queryString.length == 0)
                queryString = '&' + queryString
        }
        if (cnd) {
            queryString += 'condition=' + cnd;
            if (queryString.length == 0)
                queryString = '&' + queryString
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory?" + queryString,
            contentType: "application/json",
            data: ''
        });
        ajax.done(function(res) {
            //flash_message(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Product ID</th>'
            header += '<th style="width:40%">Condition</th>'
            header += '<th style="width:40%">Quantity</th>'
            header += '<th style="width:40%">Restock Level</th>'
            header += '<th style="width:10%">Available</th></tr>'
            $("#search_results").append(header);
            var firstInv = "";
            for(var i = 0; i < res.length; i++) {
                var inv = res[i];
                var row = "<tr><td>"+inv.product_id+"</td><td>"+inv.condition+"</td><td>"+inv.quantity+"</td><td>"+inv.restock_level+"</td><td>"+inv.available+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstInv = inv;
                }
            }
            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstInv != "")
                update_form_data(firstInv)
            flash_message("Success")
        });
        ajax.fail(function(res) {
            flash_message(res.responseJSON.message)
        });
    });*/

    // ****************************************
    // Delete a Inventory
    // ****************************************

    $("#delete-btn").click(function () {

        var pid = $("#inventory_product_id").val();
        var cnd_val = $("#inventory_condition").val();
        var cnd = "new";
        if (cnd_val == "used")
            cnd = "used"
        else if (cnd_val == "open-box")
            cnd = "open box";

        if (pid && cnd) {
            var ajax = $.ajax({
                type: "DELETE",
                url: "/inventory/" + pid + "/condition/" + cnd,
                contentType: "application/json",
                data: '',
            });
            ajax.done(function(res) {
                clear_form_data()
                flash_message("Inventory has been Deleted!")
            });
            ajax.fail(function(res) {
                flash_message("Server error!")
            });
        }
        else {
            flash_message('Product ID AND Condition is required')
        }
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#inventory_product_id").val("");
        clear_form_data()
    });

})
