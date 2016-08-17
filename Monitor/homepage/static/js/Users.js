$(document).ready(function() {
    getUserList();
});

function getUserList(){
    $.ajax({
            url: "api/userlist",
            type: "GET",
            success: function(users){
                for (var i =0; i < users.length; i++){
                    var str = "<a href=new/"+users[i].name+" class='list-group-item'>" + users[i].name + "</a>";
                    $(".my-list").append(str);
                }}
            });

}
