$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Tabs switching
    $( "#tabs" ).tabs();

    // Updates the form with data from the response
    function update_form_data(res) {
        const start_date = to_date_string(parseInt(res.start_date));
        const expiry_date = to_date_string(parseInt(res.expiry_date));
        $("#promotion_id").val(res.id);
        $("#promotion_code").val(res.code);
        $("#promotion_percentage").val(res.percentage);
        $("#promotion_product_ids").val(res.products);
        $("#promotion_start_date").val(start_date);
        $("#promotion_expiry_date").val(expiry_date);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_code").val("");
        $("#promotion_percentage").val("");
        $("#promotion_product_ids").val("");
        $("#promotion_start_date").val("");
        $("#promotion_expiry_date").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // Date string to Timestamp
    function to_timestamp(date_str) {
        let date = new Date(date_str);
        let ts_utc =  Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
        return parseInt(Math.round(ts_utc/1000));
    }

    // Timestamp to Date string
    function to_date_string(unix_timestamp) {
        let date = new Date(unix_timestamp*1000);
        let MM = (date.getUTCMonth()+1).toString().padStart(2, "0");
        let DD = date.getUTCDate().toString().padStart(2, "0");
        let YYYY = date.getFullYear();
        return `${MM}/${DD}/${YYYY}`;
    }

    // Add a product item
    $("#add-product-btn").click(function () {
        let current_size = $("#promotion_action_products").children().length;
        $("#promotion_action_products").append(`
        <div>
            <div class="col-sm-4">
                <input id=promotion_action_product_id_${current_size+1} type="text" class="form-control product-id" placeholder="Enter Product ID">
            </div>
            <div class="col-sm-4">
                <input id=promotion_action_product_price_${current_size+1} type="text" class="form-control product-price" placeholder="Enter Product Price">
            </div>
            <div class="col-sm-4">
                <input id=promotion_action_product_new_price_${current_size+1} type="text" class="form-control product-new-price" disabled=true placeholder="New Product Price">
            </div>
        </div>`);
    });

    // Shows product new prices with action result
    function update_action_result(res) {
        res['products'].forEach((product, idx) => {
            cell = $("#promotion_action_products").children("div")[idx];
            price_cell = $(cell).find(".product-new-price");
            $(price_cell).val(parseFloat(product["price"]).toFixed(2));
        });
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {

        const code = $("#promotion_code").val();
        const percentage = $("#promotion_percentage").val();
        const products_str = $("#promotion_product_ids").val();
        const start_date = to_timestamp($("#promotion_start_date").val());
        const expiry_date = to_timestamp($("#promotion_expiry_date").val());

        const products = products_str.replace(" ", "").split(",");

        const data = {
            "code": code,
            "percentage": percentage,
            "products": products,
            "start_date": start_date,
            "expiry_date": expiry_date,
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {

        const promotion_id = $("#promotion_id").val();
        const code = $("#promotion_code").val();
        const percentage = $("#promotion_percentage").val();
        const products_str = $("#promotion_product_ids").val();
        const start_date = to_timestamp($("#promotion_start_date").val());
        const expiry_date = to_timestamp($("#promotion_expiry_date").val());

        const products = products_str.replace(" ", "").split(",");

        const data = {
            "code": code,
            "percentage": percentage,
            "products": products,
            "start_date": start_date,
            "expiry_date": expiry_date,
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/promotions/" + promotion_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        let promotion_id = $("#promotion_id").val();
        if (promotion_id == false) {
            flash_message("Please input a valid Promotion ID")
            return
        }

        let ajax = $.ajax({
            type: "GET",
            url: "/promotions/" + promotion_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Promotion
    // ****************************************

    $("#delete-btn").click(function () {

        let promotion_id = $("#promotion_id").val();
        if (promotion_id == false) {
            flash_message("Please input a valid Promotion ID")
            return
        }

        let ajax = $.ajax({
            type: "DELETE",
            url: "/promotions/" + promotion_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Promotion has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {

        let code = $("#promotion_code").val();

        let queryString = ""

        if (code) {
            queryString += 'promotion-code=' + code
        }

        let ajax = $.ajax({
            type: "GET",
            url: "/promotions?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            let header = '<thead><tr>'
            header += '<th style="width:20%">ID</th>'
            header += '<th style="width:10%">Code</th>'
            header += '<th style="width:10%">Percentage</th>'
            header += '<th style="width:10%">Start Date</th>'
            header += '<th style="width:10%">Expiry Date</th>'
            header += '<th style="width:10%">Products</th></tr></thead>'
            $("#search_results").append(header);
            let firstPromotion = "";
            for(let i = 0; i < res.length; i++) {
                let promotion = res[i];
                const start_date = to_date_string(parseInt(promotion.start_date));
                const expiry_date = to_date_string(parseInt(promotion.expiry_date));
                let row = "<tr><td>"+promotion.id+"</td><td>"+promotion.code+"</td><td>"+promotion.percentage+"</td><td>"+start_date+"</td><td>"+expiry_date+"</td><td>"+promotion.products+"</td><td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Apply a Promotion
    // ****************************************

    $("#apply-btn").click(function () {

        const promotion_id = $("#promotion_action_id").val();
        const products = [];

        $('#promotion_action_products').children('div').each(function () {
            id = $(this).find('.product-id').val();
            price = $(this).find('.product-price').val();
            products.push({"product_id": id, "price": price});
        });

        const data = {
            "products": products,
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/promotions/" + promotion_id + '/apply',
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_action_result(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

})
