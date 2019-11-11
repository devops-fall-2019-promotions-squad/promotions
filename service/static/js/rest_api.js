$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_code").val(res.code);
        $("#promotion_percentage").val(res.percentage);
        $("#promotion_products").val(res.products);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_code").val("");
        $("#promotion_percentage").val("");
        $("#promotion_products").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

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
            //alert(res.toSource())
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
            // alert(res.toSource())
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
                let row = "<tr><td>"+promotion.id+"</td><td>"+promotion.code+"</td><td>"+promotion.percentage+"</td><td>"+promotion.start_date+"</td><td>"+promotion.expiry_date+"</td><td>"+promotion.products+"</td><td></tr>";
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

})
