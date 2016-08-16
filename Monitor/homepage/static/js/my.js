
$(document).ready(function() {
    loadFiles(window.location.pathname.slice(1,window.location.pathname.length));
});
var flags = {'New':"label-info", 'Changed':'label-warning', 'Checked':'label-success', 'Removed':'label-danger'};
function loadFiles(username){
        console.log("working on files @", username);
        $.ajax({
            url: "api/flagfiles/" + username,
            type: "GET",
            success: function(files){
            console.log(files[0].path.split(".")[files[0].path.split(".").length-1]);
                for (var i =0; i < files.length; i++){
                    $(".my-tbody").append("<tr>\n<th scope='row'>"+i+"</th>\n<td><span class=" + ("'label " + flags[files[i].flag]) +  "'>" + files[i].flag +"</span></td>" +  "<td>" + files[i].path +
                   "</td>\n<td>" + files[i].path.split(".")[files[i].path.split(".").length-1] + "</td>")

                }}
            });
    }