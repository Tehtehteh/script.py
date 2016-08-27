$(document).ready(function () {
    getUserList();
    $('.btn-filter').on('click', function () {
      var $target = $(this).data('target');
      if ($target != 'all') {
        $('tbody tr').css('display', 'none');
        $('tbody tr[data-status="' + $target + '"]').fadeIn('slow');
      } else {
        $('tbody tr').css('display', 'none').fadeIn('slow');
      }
    });
 });
 function getUserList(){
    $("#users-table").addClass("hidden");
    $.ajax({
        url: "/api/userlist",
        type: "GET",
        success: function(userList){
            for(let i = 0; i < userList.length; i++){
                var str = `
                <tr data-status='{0}'>
                    <td>
                      {1}
                    </td>
                    <td>
                      <div class='media'>
                        <a href="{2}" class="pull-left">
                          <img src='static/img/user.png' class='media-photo'></img>
                        </a>
                        <h4 class="title">
                          {3}
                        </h4>
                    <p class="summary">У этого пользователя {4} файлов.</p>
                </tr>
                `;
                str = str.format(userList[i].Changed?'changed':'checked',(i+1),('/new/' + userList[i].name), userList[i].name, userList[i].count);
                $(".fa").addClass('hidden');
                $('#users-table').removeClass('hidden');
                $("#users-table").append(str);
            }
        }
    })
 }

 /* "{0}{1}".format(20,16) -> "2016" */
 String.prototype.format = function() {
    var formatted = this;
    for( var arg in arguments ) {
        formatted = formatted.replace("{" + arg + "}", arguments[arg]);
    }
    return formatted;
};