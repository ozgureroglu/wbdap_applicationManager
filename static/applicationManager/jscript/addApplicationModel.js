/**
 * Created by ozgur on 6/10/15.
 */


$(document).ready(function () {


    $("#addFieldToForm").click(function () {
        addField();
    });
    jQuery('body').on("click", ".fieldRow_delete", function () {
        alert("like");
    });

    function addField(argument) {

        var table = document.getElementById("modelAdditionForm");
        var currentIndex = table.rows.length;
        // Create an empty <tr> element and add it to the 1st position of the table:
        var row = table.insertRow(table.rows.length);
        row.setAttribute('id',"fieldRow"+currentIndex);

        // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);

        var input = document.createElement("input");
        input.setAttribute('name',"field"+currentIndex);
        input.setAttribute('class','form-control');


        var select = document.createElement("select");
        select.setAttribute('class','form-control');
        var op1 = document.createElement("option");
        op1.setAttribute('value','volvo');
        op1.innerHTML='aa';
        select.appendChild(op1);


        var op2 = document.createElement("option");
        op2.setAttribute('value','CharField');
        op2.innerHTML='CharField';
        select.appendChild(op2);



        var remove = document.createElement("a");
        remove.setAttribute('href',"#");


        var span = document.createElement("i");
        span.setAttribute('class',"fa fa-remove fieldRow_delete");
        span.setAttribute('data-remove',"fieldRow"+currentIndex);

        remove.appendChild(span);

        // Add some text to the new cells:
        cell1.innerHTML = "Field: ";
        // cell2.innerHTML = row;
        cell2.appendChild(input);
        cell3.appendChild(select);
        cell4.appendChild(remove);
    }

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
// //            type: $("form[data-formId=" + formId + "]").attr('method'),
//                        url: postURL,
// //          data:{ worker:user, task:bid, workStartTime:start, workStopTime:end }
// //            data: values
// //            data:{}
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


});




