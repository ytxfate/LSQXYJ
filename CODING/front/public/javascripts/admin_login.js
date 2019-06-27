$(function () {
  $.ajax({
    method: 'post',
    async: false,
    cache: false,
    xhrFields: {
      withCredentials: true
    },
    crossDomain: true,
    dataType: "json",
    url: '/api/admin/get_login_status',
    success: function (res) {
      if (res.login_stat === "ERROR") {
        window.open('/admin', target = '_self');
      } else {
        $('#admin_name').text(res.username || 'admin');
      }
    },
    error: function () {
      console.log('error');
    }
  })
});