$(document).ready(function(){

        $(".accordion").stickUp();


        $("#home").click(function(e){
            e.preventDefault();
            minisize();
            
        });

        $(".funcs-item").click(function(){
            var uri = $(this).attr("src");
            var title = $(this).attr("name");
            minisize();
            $("#content").append("<div class='row-fluid'><div class='box span12'><div class='box-header well'><h2><i class='icon-info-sign'></i> "+ title +"</h2><div class='box-icon'><a href='#' class='btn btn-minimize btn-round'><i class='icon-chevron-up'></i></a><a href='#' class='btn btn-close btn-round'><i class='icon-remove'></i></a></div></div><div class='box-content' id='content-box'><iframe id='frame-content' scrolling='auto' frameborder='0' width='100%'' src="+uri+"></iframe><div class='clearfix'></div></div></div></div>");
            frame_load();
        });


});


    function minisize(){
        $(".box-content").each(function(){
            if($(this).is(':visible'))
            {                    
                $('.icon-chevron-up').removeClass('icon-chevron-up').addClass('icon-chevron-down');
                $(this).slideToggle();
            }
            });
    }

    function frame_load(){
               $("iframe").load(function(){       
                var height = $(this).contents().find("body").height();  
                $(this).height( height < 550 ? 550 : height );  
            });
    };