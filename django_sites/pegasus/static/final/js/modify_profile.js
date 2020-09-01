$('#defaultCheckid_first_name').click(function(){
    if ($('#defaultCheckid_first_name').prop("checked")) {
        $('#id_first_name').prop('readonly', false);
    } else {
        $('#id_first_name').prop('readonly', true);
    }      
});    

$('#defaultCheckid_last_name').click(function(){
    if ($('#defaultCheckid_last_name').prop("checked")) {
        $('#id_last_name').prop('readonly', false);
    } else {
        $('#id_last_name').prop('readonly', true);
    }      
});       

$('#defaultCheckid_date_of_birth').click(function(){
    if ($('#defaultCheckid_date_of_birth').prop("checked")) {
        $('#id_date_of_birth').prop('readonly', false);
        counter2 -=1;
    } else {
        $('#id_date_of_birth').prop('readonly', true);
        counter2 +=1;
    }      
});       

$('#defaultCheckid_physical_address').click(function(){
    if ($('#defaultCheckid_physical_address').prop("checked")) {
        $('#id_physical_address').prop('readonly', false);
    } else {
        $('#id_physical_address').prop('readonly', true);
    }      
});     

$('#defaultCheckid_city').click(function(){
    if ($('#defaultCheckid_city').prop("checked")) {
        $('#id_city').prop('readonly', false);
    } else {
        $('#id_city').prop('readonly', true);
    }      
});  

$('#defaultCheckid_state').click(function(){
    if ($('#defaultCheckid_state').prop("checked")) {
        $('#id_state').prop('readonly', false);
    } else {
        $('#id_state').prop('readonly', true);
    }      
}); 

$('#defaultCheckid_zip_code').click(function(){
    if ($('#defaultCheckid_zip_code').prop("checked")) {
        $('#id_zip_code').prop('readonly', false);
    } else {
        $('#id_zip_code').prop('readonly', true);
    }      
}); 

$('#defaultCheckid_phone_number').click(function(){
    if ($('#defaultCheckid_phone_number').prop("checked")) {
        $('#id_phone_number').prop('readonly', false);
    } else {
        $('#id_phone_number').prop('readonly', true);
    }      
});

$('#defaultCheckid_email').click(function(){
    if ($('#defaultCheckid_email').prop("checked")) {
        $('#id_email').prop('readonly', false);
    } else {
        $('#id_email').prop('readonly', true);
    }      
}); 

$('#defaultCheckid_username').click(function(){
    if ($('#defaultCheckid_username').prop("checked")) {
        $('#id_username').prop('readonly', false);
    } else {
        $('#id_username').prop('readonly', true);
    }      
});

$('#defaultCheckid_bio').click(function(){
    if ($('#defaultCheckid_bio').prop("checked")) {
        $('#id_bio').prop('readonly', false);
    } else {
        $('#id_bio').prop('readonly', true);
    }
});

$('#defaultCheckid_profile_picture').click(function(){
    if ($('#defaultCheckid_profile_picture').prop("checked")) {
        $('#id_profile_picture').prop('readonly', false);
        counter11 -=1;
    } else {
        $('#id_profile_picture').prop('readonly', true);
        counter11 +=1;
    }
});

