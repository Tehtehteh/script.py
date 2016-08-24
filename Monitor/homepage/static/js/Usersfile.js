$(document).ready(function() {
  loadFiles(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
  loadFilesCount(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
  loadFlagFilesCount(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
  
  $('.accordion').click(function(){
    $(this).toggleClass('active').next().slideToggle('fast');
  }).next().hide();
});

var flags = {'New':"label-info", 'Changed':'label-warning', 'Checked':'label-success', 'Removed':'label-danger'};
var flagcount = {"Changed" : 0, "Removed": 0, "New":0, "Checked" : 0};
$('.badge-info').popover({ trigger: "hover" });
$('[data-toggle="popover"]').popover();

function loadFlagFilesCount(username){
    $.ajax({
        url: "/api/flagfiles/" + username,
        type: "GET",
        success: function(files){
            for (let i = 0; i < files.length; i ++){
            flagcount[files[i].flag] ++ ;}
            for (x in flagcount){
                $(".badge-"+x).text(flagcount[x]);}
            flagcount = {"Changed" : 0, "Removed": 0, "New":0, "Checked" : 0};
        },

    })

}
function sendRequestForChanges (username, fileList, isolateList, csrf_token, callback) {
        setTimeout(function() {
            $.ajax({
                url: '/api/accept/' + username,
                dataType: 'json',
                data: {'fileList':JSON.stringify(fileList, null, ' '),
                        csrfmiddlewaretoken: csrf_token,
                        'isolate':JSON.stringify(isolateList, null, ' ')
                        },
                type: "POST",
                success:function(data){
                    if (callback) callback(null, data);
                },
                error: function(status, err){
                    if (callback) callback(err);
                }
            });
        }, 2000);
    }

var refresh = 'fa fa-refresh refresh';
var stopEvents = false;
function acceptChanges(username, csrf_token){
    var fileList = [];
    var isolateList = [];
    var boxes = $(":checkbox");
    for (let i = 0; i < boxes.length; i++) {
        if ($(boxes[i]).prop('checked')) {
        fileList.push(boxes[i].value)
        }}
    var QuarList = $("#Checked input:checkbox");
    for (let i = 0; i<QuarList.length; i++){
        if ($(QuarList[i]).prop("checked")){
            isolateList.push(QuarList[i].value);
        }
    }
    if (!stopEvents) {
        stopEvents = true;
        $(".my-badge").addClass("hidden");
        $(".fa").removeClass("hidden");
        sendRequestForChanges(username, fileList, isolateList, csrf_token, function(err, data) {
            for(x in flags){
                $("#"+x).empty();
            }
            loadFlagFilesCount(username);
            loadFiles(username);
            loadFilesCount(username);
            stopEvents = false;
        });
    }
}

function loadFiles(username){
        $.ajax({
            url: "/api/flagfiles/" + username,
            type: "GET",
            success: function(files){
                for (var i =0; i < files.length; i++){
                    var str = "<tr>\n<th scope='row'>"+(i+1)+"</th>\n<td>" + '<input type="checkbox" name="ignore"  value="'+files[i].path+'">' + "</td>"+  "<td>" + files[i].path +
                   "</td>\n<td>" + files[i].path.split(".")[files[i].path.split(".").length-1] + "</td>" + "<td>" + new Date(files[i].date) + "</td>";
                    $("#"+files[i].flag).append(str);
                }}
            });
    }

function loadFilesCount(username){
    $('.my-badge').text('').addClass('hidden');
    $(".fa").removeClass('hidden');
    $.ajax({
        url: "/api/userlist",
        type: "GET",
        success: function(users){
            for (let i = 0; i<users.length; i++){
                if (users[i].name == username.split("#")[0]){
                    $(".badge-count").text(users[i].count);
                    break;
                }
            }
            $(".fa").addClass('hidden');
            $('.my-badge').removeClass('hidden');
        }
    })
}