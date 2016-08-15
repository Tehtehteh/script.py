
$(document).ready(function() {
loadFiles(window.location.pathname.slice(1,window.location.pathname.length));
});

function loadFiles(username){
        console.log("working on files @", username);
        $.ajax({
            url: "api/files/" + username,
            type: "GET",
            success: function(files){
                for (var i =0; i < files.length; i++){
                    $("<tr>\n<th scope='row'>" + (i+1) + "</th>\n" + getFlag(files[i]) + "<td>" + files[i].path +
                    "</td>\n<td>" + files[i].path.split(".")[files[i].path.split(".").length-1] + "</td>").hide().appendTo(".my-tbody").fadeIn(i*20 + 1000);

                }}
            });
    }
function getFlag(file){
        if (file.old_hash!="" && file.new_hash!=""){
           return "<td><span class=\"label label-warning\">Changed</span></td>";
        }
        else if (file.flag_exists == 0){
            return "<td><span class=\"label label-danger\">Removed</span></td>";
        }
        else if (file.old_hash == file.new_hash || file.old_hash!="" && file.new_hash=="") {
            return "<td><span class=\"label label-success\">Checked</span></td>";
        }
        else if (file.old_hash=="" && file.flag_exists == 1) {
            return "<td><span class=\"label label-info\">New</span></td>"
        }
    }