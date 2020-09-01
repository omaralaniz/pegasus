$('#hometab').click(function(){
    $('#home').addClass('active')
    $('#listing').removeClass('active');     
});

$('#listingtab').click(function(){
        $('#listing').addClass('active');
        $('#home').removeClass('active');     
});