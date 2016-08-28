$(document).ready(function(){
  loadFiles(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
  loadFilesCount(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
  loadFlagFilesCount(window.location.toString().split("/")[window.location.toString().split("/").length-1]);
  getQuote();
  $('.accordion').click(function(){
    $(this).toggleClass('active').next().slideToggle('fast');
  }).next().hide();
});

var flags = {
  'New': 'label-info',
  'Changed': 'label-warning',
  'Checked': 'label-success',
  'Removed': 'label-danger'
};

var flagcount = { 'Changed': 0, "Removed": 0, "New": 0, "Checked": 0 };

$('.badge-info').popover({ trigger: "hover" });
$('[data-toggle="popover"]').popover();

function loadFlagFilesCount(username) {
  $.ajax({
    url: "/api/flagfiles/" + username,
    type: "GET",
    success: function(files) {
      for (let i = 0; i < files.length; i++) flagcount[files[i].flag]++;
      for (x in flagcount) $(".badge-"+x).text(flagcount[x]);
      flagcount = { 'Changed': 0, 'Removed': 0, 'New': 0, 'Checked': 0 };
    },
  });
}

function sendRequestForChanges(username, fileList, isolateList, csrf_token, callback) {
  setTimeout(function(){
    $.ajax({
      url: '/api/accept/' + username,
      dataType: 'json',
      data: {
        'fileList': JSON.stringify(fileList, null, ' '),
        'isolate': JSON.stringify(isolateList, null, ' '),
        'csrfmiddlewaretoken': csrf_token
      },
      type: 'POST',
      success: function(data){ if (callback) callback(null, data); },
      error: function(status, err){ if (callback) callback(err); }
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
    if ($(boxes[i]).prop('checked')) fileList.push(boxes[i].value);
  }
  var QuarList = $("#Checked input:checkbox");
  for (let i = 0; i<QuarList.length; i++){
    if ($(QuarList[i]).prop("checked")) isolateList.push(QuarList[i].value);
  }
  if (!stopEvents) {
    stopEvents = true;
    $(".my-badge").addClass("hidden");
    $(".fa").removeClass("hidden");
    sendRequestForChanges(username, fileList, isolateList, csrf_token, function(err, data) {
      for(x in flags) $("#"+x).empty();
      loadFlagFilesCount(username);
      loadFiles(username);
      loadFilesCount(username);
      stopEvents = false;
    });
  }
}
$.fn.multiline = function(text){
    this.text(text);
    this.html(this.html().replace(/\n/g,'<br/>'));
    return this;
}
function getQuote(){
    $('.fa').removeClass('hidden');
    $.ajax({
        url: '/api/getquote',
        type: 'GET',
        success: function(quote){
            $('.fa').addClass('hidden');
            $('.text').multiline(quote.quote)
        }
    })
}

function loadFiles(username){
  $.ajax({
    url: "/api/flagfiles/" + username,
    type: "GET",
    success: function(files){
      for (var i = 0; i < files.length; i++){
        var str = `
          <tr><th scope='row'>{0}</th>
          <td><input type='checkbox' name='ignore' value='{1}'></td>
          <td>{2}</td> <td>{3}</td> <td>{4}</td>`;
        str = str.format(
          i+1,
          files[i].path,
          files[i].path,
          files[i].path.split(".")[files[i].path.split(".").length-1],
          new Date(files[i].date)
        );
        
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

/* "{0}{1}".format([20,16]) -> "2016" */
String.prototype.format = function() {
    var formatted = this;
    for( var arg in arguments ) {
        formatted = formatted.replace("{" + arg + "}", arguments[arg]);
    }
    return formatted;
};