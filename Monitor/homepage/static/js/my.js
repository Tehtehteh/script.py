
$(document).ready(function() {
    loadFiles(window.location.pathname.slice(1,window.location.pathname.length));
    loadFilesCount(window.location.pathname.slice(1,window.location.pathname.length));
});
var flags = {'New':"label-info", 'Changed':'label-warning', 'Checked':'label-success', 'Removed':'label-danger'};

function loadFiles(username){
        console.log("working on files @", username);
        $.ajax({
            url: "api/flagfiles/" + username,
            type: "GET",
            success: function(files){
            console.log("ASDFDSFSDFD")
                for (var i =0; i < files.length; i++){
                    var str = "<tr>\n<th scope='row'>"+(i+1)+"</th>\n<td><span class=" + ('"label ' + flags[files[i].flag]) +  '">' + files[i].flag +"</span></td>" +  "<td>" + files[i].path +
                   "</td>\n<td>" + files[i].path.split(".")[files[i].path.split(".").length-1] + "</td>";
                    $(".my-tbody").append(str);

                }}
            });
    }

function loadFilesCount(username){
    $.ajax({
        url: "api/userlist",
        type: "GET",
        success: function(users){
            for (let i = 0; i<users.length; i++){
                if (users[i].name == username){
                    $(".my-badge").append(users[i].count);
                    break;
                }
            }
        }
    })
}