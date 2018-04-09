///**
// * Created by ozgur on 6/10/15.
// */
//
//
//
///**
// * Created by ozgur on 12/21/14.
// */
//
//$(document).ready(function () {
//
//    var edit_icon = $(".fa-pencil-square-o"); //Add button ID
//
//
//    $(edit_icon).click(function () {
//
//
//        var buttonId = this.getAttribute('icon-id');
//        alert(buttonId);
//        var csrftoken = $("[name*='csrfmiddlewaretoken']").val();
//        alert(csrftoken);
//
//
//                    //Kullanici OK verdigi icin soruyu silmek uzere bir ajax post yapalim
//                    // Lets first setup the ajax request
//                    $.ajaxSetup({
//                        beforeSend: function (xhr, settings) {
//                            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
//                                // Send the token to same-origin, relative URLs only.
//                                // Send the token only if the method warrants CSRF protection
//                                // Using the CSRFToken value acquired earlier
//                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
//                                //alert("beforeSend");
//
//                            }
//                        }
//                    });
//
//                    var postURL = "editApplication/" + buttonId + "/";
//                    //alert(postURL);
//                    $.ajax({
//                        //beforeSend: function (xhr, opts) {
//                        //    $("#dialog-confirm").dialog({
//                        //        resizable: false,
//                        //        height: 140,
//                        //        modal: true,
//                        //        buttons: {
//                        //            "Delete all items": function () {
//                        //                $(this).dialog("close");
//                        //            },
//                        //            Cancel: function () {
//                        //                $(this).dialog("close");
//                        //                xhr.abort();
//                        //            }
//                        //        }
//                        //    });
//                        //},
//
//                        //beforeSend:function(){
//                        //
//                        //},
//
//                        type: "GET",
////            type: $("form[data-formId=" + formId + "]").attr('method'),
//                        url: postURL,
////          data:{ worker:user, task:bid, workStartTime:start, workStopTime:end }
////            data: values
////            data:{}
//
//                        error: function () {
//                            //ShowStatus("AJAX - error()");
//
//                            // Load the content in to the page.
//                            //jContent.html("<p>Page Not Found!!</p>");
//                        },
//
//
//                        complete: function () {
//                            //ShowStatus("AJAX - complete()");
//                            //alert('complete')
//                        },
//
//                        success: function () {
//                            //alert('sucess')
//                        }
//                    }).done(function (msg) {
//                        //location.reload(true)
//                        $("#id_table_row_" + buttonId).remove();
//                        //alert(" Your comment has been saved. ");
//                    });
//
//    });
//
//
//});
//
//
//
//
