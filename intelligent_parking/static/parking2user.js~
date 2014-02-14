
$(document).ready(function(){

    change_user_parking();

    $("#unused-parking-dialog").dialog({
        modal:false,
        autoOpen:false,
        width:800,
        maxWidth:1000,
        maxHeight:450,
        position:[200,100],
    });

      $("#unused-user-dialog").dialog({
        modal:false,
        autoOpen:false,
        width:800,
        maxWidth:1000,
        maxHeight:450,
        position:[200,100],
    });


	$('#street').change(function(){

            change_parking_list();
	
	});


    $('#user').change(function(){
         
            change_user_parking();

    });


    $("#to-user").click(function(){
            change_to_user();
            
    });

    $("#delete-parking").click(function(){
            change_delete_parking();
    });

    $("#unused-parking").click(function(){
            change_unused_parking();
            $("#unused-parking-dialog").dialog("open");
    });

    $("#unused-user").click(function(){
            change_unused_user();
            $("#unused-user-dialog").dialog("open");
    });

});

function change_parking_list(){

        var sValue = $('#street').val();
        var uValue = $('#user').val();
        
        $.ajax({
                    url: "/pc/ajax/getstreetparkinglist"+"?street_id="+sValue+"&user_id="+uValue,
                    dataType: "json",
                    success: function (r) {
                        $("#parking-list").html("");  
                        $(r).each(function (index) {
                            var parking = r[index];
                            $("#parking-list").append("<option value=" + parking.f_id + ">" + parking.f_name + "</option>");
                        });
                    }});

};

function change_user_parking(){

     var uValue = $('#user').val();
    
        $.ajax({
                    url:"/pc/ajax/getuserparkinglist/" + uValue,
                    dataType:"json",
                    success:function(r){
                        $("#user-parking-list").html("");

                        $(r).each(function(index)
                        {
                            var parking = r[index];
                            $("#user-parking-list").append("<option value=" + parking.f_parking_id + ">" + parking.f_parking_name + "</option>" )
                        });

                        change_parking_list();
                        
                    }});  

};

function change_to_user(){
    var user_id = $("#user").val();
    var user_name = $("#user").find("option:selected").text();
    var parking_ids = $("#parking-list").val();

    if (parking_ids ==null)
    {
        alert("未选择任何车位!");
        return false;
    }else
    {
        var cf = confirm("确定将以上车位分配给"+user_name+"?");
        if(cf == true)
        {
            if (parking_ids ==null) {alert("未选择任何车位!");return false;};
            $.ajax({
                type:"POST",
                url:"/pc/ajax/mapparking2user",
                data:{user_id:user_id, parking_ids:parking_ids.join(",")},
                dataType:"json",
                failure: function () {//请求失败处理函数  
                    alert('请求失败');
                },
                success:function(r){
                    change_user_parking();
                    change_unused_user();
                    change_unused_parking();
                    
                }});
        }else
        {
            return false;      
        }

    }
    
};
    

function change_delete_parking(){
    var user_id = $("#user").val();
    var user_name = $("#user").find("option:selected").text();
    var parking_ids = $("#user-parking-list").val();

    if (parking_ids ==null)
    {
        alert("未选择任何车位!");
        return false;
    }else
    {
        var cf = confirm("确定将以上车位从"+user_name +"的列表中删除?");
        if(cf==true)
        {
         
            $.ajax({
                type:"POST",
                url:"/pc/ajax/removeparking4user",
                data:{user_id:user_id, parking_ids:parking_ids.join(",")},
                dataType:"json",
                failure: function () {//请求失败处理函数  
                    alert('请求失败');
                },
                success:function(r){
                    
                    change_user_parking();
                    change_unused_user();
                    change_unused_parking();
                
            }});
        }else
        {
            return false;
        }
    }
    
    
    
};

function change_unused_parking(){
    $.ajax({
        url:"/pc/ajax/getunusedparkinglist"+"?"+"t="+Math.random(),
        dataType:"json",
        success:function(r){
            $("#unused-parking-dialog").html("");

            $(r).each(function(index)
            {
                   $("#unused-parking-dialog").append("<li style='float:left'>" +r[index].f_name + "</li>");                   
            });


        }
    });
};

function change_unused_user(){

    $.ajax({
        url:"/pc/ajax/getunuseduserlist"+"?"+"t="+Math.random(),
        dataType:"json",
        success:function(r){
            $("#unused-user-dialog").html("");

            $(r).each(function(index)
            {
                    $("#unused-user-dialog").append("<li style='float:left'>" + r[index].f_name + "</li>");
            });
        }
    });
};
