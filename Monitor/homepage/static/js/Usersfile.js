
$(document).ready(function() {
    loadFiles(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
    loadFilesCount(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
    loadFlagFilesCount(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
    var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
    acc[i].onclick = function(){
        this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("show");
    }
}
});
var flags = {'New':"label-info", 'Changed':'label-warning', 'Checked':'label-success', 'Removed':'label-danger'};
flagcount = {"Changed" : 0, "Removed": 0, "New":0, "Checked" : 0}

function loadFlagFilesCount(username){
    $.ajax({
        url: "/api/flagfiles/" + username,
        type: "GET",
        success: function(files){
            for (let i = 0; i < files.length; i ++){
            flagcount[files[i].flag] ++ ;}
            console.log(flagcount);
            for (x in flagcount){
                $(".badge-"+x).append(flagcount[x]);}
        }
    })

}

function loadFiles(username){
        $.ajax({
            url: "/api/flagfiles/" + username,
            type: "GET",
            success: function(files){
                for (var i =0; i < files.length; i++){
                    var str = "<tr>\n<th scope='row'>"+(i+1)+"</th>\n"  +  "<td>" + files[i].path +
                   "</td>\n<td>" + files[i].path.split(".")[files[i].path.split(".").length-1] + "</td>";
                    //$("#"+files[i].flag).append("<button type='button' class='list-group-item'>" + files[i].path + "</button>");
                    $("#"+files[i].flag).append(str);
                }}
            });
    }

function loadFilesCount(username){
    $.ajax({
        url: "/api/userlist",
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