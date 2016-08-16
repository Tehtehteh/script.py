$(document).ready(function() {
    getUserList();
});

function getUserList(){
    $.ajax({
            url: "api/userlist",
            type: "GET",
            success: function(users){
                for (var i =0; i < users.length; i++){
                    var str = "<a href="+users[i].name+"><li class='list-group-item'>" + users[i].name + "</li></a>";
                    $(".my-list").append(str);

                }}
            });

}
            <!--<a href="{{user.name}}"><li class="list-group-item">{{ user.name }}</li></a>-->
