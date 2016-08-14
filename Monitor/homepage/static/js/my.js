$(document).ready(loadFiles(username));

function loadFiles(username){
    $.ajax(){
        url: "api/files/" + username,
        type: get,
        success: function(files){
            for (var i =0; i < files.length; i++){
                $(".my-tbody").append("<tr>\n<th scope='row'>"+i+"</th>\n" + getFlag(files[i]) + "<td>" + files[i].path +
                "</td>\n<td>" + files[i].path.split(".")[1] + "</td>")
            }}
        }
}

function getFlag(file){
    switch file{
        case file.old_hash!="" &&  file.new_hash!="":{
            return "<td><span class=\"label label-warning\">Changed</span></td>";
            break;
        }
        case file.flag_exists == 0:{
            return "<td><span class=\"label label-danger\">Removed</span></td>";
            break;
        }
        case file.old_hash == file.new_hash:{
            return "<td><span class=\"label label-success\">Checked</span></td>";
            break;
        }
        default:{
            return "<td><span class=\"label label-info\">New</span></td>"
        }
    }
}