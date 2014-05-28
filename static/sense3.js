$(document).ready(function(){
    $( "#addpatform" ).submit(function( event ) {
      alert( "Handler for .submit() called." );
    });
})

var inputrowcount = 1
$(document).ready(function(){
    $('#rowadd').click(function(){
    	inputrowcount += 1

    	var rowhtml = "<tr><td><select class='selectpicker' data-style='btn-primary' name='picker1'>"
        rowhtml += "<option>Pre-baseline CT</option><option>Baseline CT/CTP/CTA</option>"
        rowhtml += "<option>Baseline MRI</option><option>DSA</option><option>12hr CT/CTP/CTA</option>"
        rowhtml += "<option>12hr MRI</option><option>5day MRI</option><option>Miscellaneous 1</option>"
        rowhtml += "<option>Miscellaneous 2</option><option>Miscellaneous 3</option>"
        rowhtml += "<option>Miscellaneous 4</option><option>Miscellaneous 5</option></select></td>"
        rowhtml += "<td><input type='file' name='file"+inputrowcount+"'></td></tr>"

        $('#inputtable').append(rowhtml)
    })
})