$(function () {
    function render_time() {
        return moment($(this).data('timestamp')).format('lll')
    }
    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    )
    $('button.reply').click(function() {
        var reply_id = $(this).attr("data-reply-id")
        console.log(reply_id)
        $.ajax({
            url: reply_url,
            type: 'get',
            data: {'comment_id':reply_id},
            success: function(data){
                // alert(data);
                $("#reply_area").html(data);
                $("#be_reply").val(reply_id);
                $("html,body").animate({scrollTop:$("#comment-form").offset().top},1000)
            }
        })
    })
    $("#reply_area").on('click',"#cancel_reply",function(){
        $("#reply_area").empty();
        $("#be_reply").val("");
    });


});


$(document).ready(function() {
    window.setTimeout(function() {
    $('.alert').fadeTo(500,0.5).slideUp(500,function(){$('.alert').remove()});
    }, 2000);

    $(window).scroll(function () {
        // alert($(window).height())
        var scrollheight = $(window).scrollTop();
        if (scrollheight > $(window).height()) {
            $('#scroll2top').fadeIn();
        } else {
            $('#scroll2top').fadeOut();
        }
    })
    $("#scroll2top").click(function () {
        $(window).scrollTop(0);
    })

    function render_time() {
        return moment($(this).data('timestamp')).format('lll')
    }

    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    )

    $('button.reply').click(function() {
        var reply_id = $(this).attr("data-reply-id")
        console.log(reply_id)
        $.ajax({
            url: reply_url,
            type: 'get',
            data: {'comment_id':reply_id},
            success: function(data){
                // alert(data);
                $("#reply_area").html(data);
                $("#be_reply").val(reply_id);
                $("html,body").animate({scrollTop:$("#comment-form").offset().top},1000)
            }
        })
    })
    $("#reply_area").on('click',"#cancel_reply",function(){
        $("#reply_area").empty();
        $("#be_reply").val("");
    });

    $("#message_form").submit(function (event) {
        event.preventDefault();
        $.ajax({
            url: message_url,
            type: 'post',
            // dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({
                name:$('#name').val(),
                body:$('#body').val()
            }),
            success: function(response){
                $('#show_message').prepend(response);
                $('#name').val("");
                $('#body').val("")
            },
            error: function(){
                console.log("something wrong about message function")
            }
        })
    })
});
