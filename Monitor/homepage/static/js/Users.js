$(document).ready(function() {
    getUserList();
});

function getUserList(){
    $.ajax({
            url: "api/userlist",
            type: "GET",
            success: function(users){
                for (var i =0; i < users.length; i++){
                    var str = "<tr>\n<th scope='row'>"+(i+1)+"</th>\n<th><a href=new/" + users[i].name + ">" + users[i].name + "</a></th>\n<td>" + users[i].count +"</td><td>" + (users[i].Changed? '  <span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span></td>' : '</td>');
                    console.log(str);
                    $("#users").append(str);
                }}
            });

}
