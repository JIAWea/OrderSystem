
$(function () {
    layui.use(['form', 'table'], function() {
        var table = layui.table;

        // 添加用户
        $('#addUserForm').on('hidden.bs.modal', function () {
            document.getElementById("backendUserAdd").reset();      // 取消添加管理员的模态对话框后清空输入框的值
        });
        // 设置密码
        $('#setPwdFrom').on('hidden.bs.modal', function () {
            document.getElementById("changepassword").reset();      // 取消更改密码的模态对话框后清空输入框的值
        });

        $("#SetPassword").click(function () {
            var old_password = $("#changepassword").find(':input[name="old_password"]').val();
            var new_password = $("#changepassword").find(':input[name="new_password"]').val();
            var repeat_password = $("#changepassword").find(':input[name="repeat_password"]').val();
            if (old_password == '') {
                layer.msg('旧密码不能为空', {icon: 2});
            } else if (new_password != repeat_password) {
                layer.msg('新密码不一致', {icon: 2})
            } else {
                $.ajax({
                    type: "POST",   //提交的方法
                    url: "/backend/admin/update/password/change/", //提交的地址
                    data: $('#changepassword').serialize(),// 序列化表单值
                    success: function (data) {  //成功
                        if (data.err_msg) {
                            layer.msg(data.err_msg, {icon: 2});  //就将返回的数据显示出来
                        } else {
                            window.location.reload();
                        }
                    },
                    error: function (request) {  //失败的话
                        layer.msg(data.err_msg, {icon: 2});
                    },
                })
            }
        });
    });

    $("#mainnav-menu li a").each(function () {
        var that = $(this);
        // if ($(that)[0].href == String(window.location)){
        if ($(that)[0].href == String(window.location).split('?')[0]) {
            if (that.parents('.collapse').hasClass('collapse')) {
                that.parent().css('background-color', '#17222d');
                that.parents('.collapse').addClass('in');
            } else {
                that.parents('li').css('background-color', '#17222d');
            }
        }
    });

});


