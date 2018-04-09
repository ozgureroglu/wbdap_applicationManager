/**
 * Created by ozgur on 1/3/16.
 */

$(document).ready(function () {

    var submitButton = $("#submitbutton");
    var form = $("#appCreateForm");

    submitButton.click(function () {
        var csrftoken = $("[name*='csrfmiddlewaretoken']").val();
        var success = this.getAttribute('data-success-url');

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

        $('#myPleaseWait').modal('show');
        $("body").css("cursor", "progress");

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            error: function () {
                //ShowStatus("AJAX - error()");
                // Load the content in to the page.
                //jContent.html("<p>Page Not Found!!</p>");
            },
            statusCode: {
                404: function () {
                    alert("page not found");
                },
                400: function () {
                    alert("bad request");
                },
                200: function () {

                    setTimeout(function () {
                        // location.reload();
                        location.href = success;
                        $('#myPleaseWait').modal('hide');
                        $("body").css("cursor", "default");
                    }, 5000);

                }
            },

            complete: function () {
                //ShowStatus("AJAX - complete()");
                //alert('complete')
            },

            success: function () {
                //alert('success')
                // setTimeout(function () {
                //     location.reload();
                // }, 2000);
            }

        }).done(function (msg) {
            //$("#id_table_row_" + buttonId).remove();
            //alert(" Your comment has been saved. ");
        });


    });

});




