/**
 * Created by ozgur on 12/4/16.
 * Deletes the selected application
 */

$(function () {

    var $table = $('#table');
    var $button = $('#button');
    var csrftoken = getCookie('csrftoken');


    $('#delete_selected').click(function () {

        var apps2delete = {};
        var res = $table.bootstrapTable('getAllSelections');

        for (i = 0; i < res.length; i++) {
            var jsobj = JSON.stringify(res[i]);
            apps2delete[i] = res[i]['4'];
        }
        data = apps2delete;

        var r = confirm("Are you sure to delete following applications?");

        if (r == true) {
            // POost data to service
            // Lets first setup the ajax request
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                        // Send the token to same-origin, relative URLs only.
                        // Send the token only if the method warrants CSRF protection
                        // Using the CSRFToken value acquired earlier
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        //alert("beforeSend");
                    }
                }
            });
            var postURL = "/applicationManager/deleteApplication/";

            $('#myPleaseWait').modal('show');
            $.ajax({
                type: "POST",
                url: postURL,
                data: data,
                error: function () {
                    //ShowStatus("AJAX - error()");
                },
                complete: function () {
                    //alert('complete')
                },
                success: function () {
                    //alert('sucess')
                    //                        setTimeout(function () {#
                }
            }).done(function (msg) {
                // alert(" Your data has been sent. ");
            });

            setTimeout(function () {
                location.reload();
                $('#myPleaseWait').modal('hide');
                $("body").css("cursor", "default");
            }, 4000);
        } else {
            alert("Delete Canceled!");
        }


    });
});