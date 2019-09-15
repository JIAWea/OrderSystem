
// csrf
function csrftoken() {
    /*********** csrftoken开始****************/
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    /*********** csrftoken结束****************/
}

// layui
layui.use(['element', 'table', 'form', 'jquery', 'laydate'], function() {
    var element = layui.element,
    table = layui.table,
    $ = layui.jquery,
    myForm = layui.form;
    laydate = layui.laydate;
    // formSelects = layui.formSelects;

    element.on('tab(tabBrief)', function(data){
        //当前Tab标题所在的原始DOM元素 this
    });

    searchSelect();

    //日期范围
    laydate.render({
        elem: '#member_expiry_time'
        ,format: 'MM/dd/yyyy'
        ,range: '~'
    });
    laydate.render({
        elem: '#order_first_time'
        ,format: 'MM/dd/yyyy'
        ,range: '~'
    });
    laydate.render({
        elem: '#comment_last_time'
        ,format: 'MM/dd/yyyy'
    });


    var tableObj = table.render({
        elem: '#tbBuyers'
        // ,url: '/api/v1/buyers/'
        ,url: '/backend/buyers/view/'
        ,cellMinWidth: 80
        ,page: true                                    //开启分页
        ,limit: 20
        ,limits: [10,20,30]
        ,defaultToolbar: []
        ,cols: [[
            {type: 'checkbox', width: 50}
            ,{field:'index', title: '序号', type: 'numbers', width: 50}
            ,{field:'number', title: '买家编号', width: 100, templet: function (d) {
                    return  '<a name="redirect" href="/backend/buyers/edit/detail/'+ d.id +'" class="layui-table-link">'+ d.number +'</a>'
            }}
            ,{field:'buyer_status', title: '买家状态', width: 100}
            ,{field:'member_type', title: '会员类别', width: 100}
            ,{field:'member_expiry_time', title: '会员过期时间', width: 120}
            ,{field:'buyer_phone', title: '注册手机'}
            ,{field:'buyer_email', title: '注册邮箱'}

            ,{field:'one_year_price', title: '12月累计信用卡金额', width: 150}
            ,{field:'order_vaild_price', title: '累计有效订单金额', width: 150}
            ,{field:'review_count', title: 'Review数量', width: 120}
            ,{field:'review_percent', title: '留评比', width: 120}
            ,{field:'order_first_time', title: '首单时间', width: 120}
            ,{field:'review_last_time', title: '最后评价时间', width: 120}
            ,{align:'center', toolbar: '#barTable', width: 150, fixed: 'right'}
        ]]
    });

    //监听行工具事件
    table.on('tool(line-tool)', function(obj){ //注：tool 是工具条事件名，test 是 table 原始容器的属性 lay-filter="对应的值"
        var data = obj.data //获得当前行数据
        ,layEvent = obj.event; //获得 lay-event 对应的值

        var mobile_flag = isMobile();

        if(layEvent === 'edit'){
            var area = null;
            if(mobile_flag){
                area = ['100%', '100%']
            }else {
                area = ['50%', '700px']
            }

            layer.open({
                type    : 1,
                title   : '编辑买家信息',
                area    : area,
                fixed   : false, //不固定
                maxmin  : true,
                offset  : 't',
                content : $("#editInfo"),
                // btn     : ['确认', '取消'],
                success : function(index, layero) {             // 成功弹出后回调
                    $("#editInfo").attr('edit-id', data.id);

                    laydate.render({
                        elem: '#m_expiry_time'
                        ,format: 'MM/dd/yyyy'
                    });
                    laydate.render({
                        elem: '#o_first_time'
                        ,format: 'MM/dd/yyyy'
                    });
                    laydate.render({
                        elem: '#c_last_time'
                        ,format: 'MM/dd/yyyy'
                    });

                    laydate.render({
                       elem: '#m_expiry_time'
                       ,value: data.member_expiry_time
                    });

                    laydate.render({
                       elem: '#o_first_time'
                       ,value: data.order_first_time
                    });

                    laydate.render({
                       elem: '#c_last_time'
                       ,value: data.review_last_time
                    });

                    myForm.val('editForm', {
                        number: data.number,
                        buyer_status: data.buyer_status,
                        member_status: data.member_status,
                        member_type: data.member_type,
                        // member_expiry_time: data.member_expiry_time,
                        buyer_phone: data.buyer_phone,
                        buyer_email: data.buyer_email,
                        one_year_price: data.one_year_price,
                        order_vaild_price: data.order_vaild_price,
                        review_count: data.review_count,
                        review_percent: data.review_percent,
                    });

                },
                cancel  : function(index, layero){
                    layer.close(index);
                    // 清空编辑表单的值
                    document.getElementById("editInfo").reset();
                    //return false 开启该代码可禁止点击该按钮关闭
                }
            })
        }else if(layEvent === 'del'){
            layer.confirm('是否要删除，删除后不可恢复', {title: '确认删除',icon: 2}, function(index){
                csrftoken();
                $.ajax({
                    url:'/backend/buyers/delete/' + data.id,
                    dataType:'JSON',
                    type:'delete',
                    success:function (arg) {
                       if(arg.status){
                            layer.msg('删除成功');
                            tableObj.reload()
                        }else {
                            layer.msg(arg.msg);
                            tableObj.reload()
                        }
                    },
                    error :function (arg) {
                         //get the status code
                        if (arg.status == 403) {
                            layer.msg(arg.responseText, {icon: 2})
                        } else {
                            layer.msg('删除失败', {icon: 2});
                        }
                    }
                })
            });
        }
    });

    // 监听提交筛选
    myForm.on('submit(sreachBtn)', function(data){
        // layer.alert(JSON.stringify(data.field), {
        //     title: '最终的提交信息'
        // });
        var platform = data.field.platform;
        var site = data.field.site;
        var buyer_status = data.field.buyer_status;
        var cc = data.field.cc;
        var order_vaild = data.field.order_vaild;
        var member_type = data.field.member_type;
        var review = data.field.review;
        var comment_percent = data.field.comment_percent;
        var buyer_number = data.field.buyer_number;
        var buyer_phone = data.field.buyer_phone;
        var buyer_email = data.field.buyer_email;
        var member_expiry_time = data.field.member_expiry_time;
        var order_first_time = data.field.order_first_time;
        var comment_last_time = data.field.comment_last_time;

        var condition = new Object();
        if(platform){
            condition.platform = platform
        }
        if(site){
            condition.site = site
        }
        if(buyer_status){
            condition.buyer_status = buyer_status
        }
        if(cc){
            condition.cc = cc
        }
        if(order_vaild){
            condition.order_vaild = order_vaild
        }
        if(site){
            condition.site = site
        }
        if(member_type){
            condition.member_type = member_type
        }
        if(review){
            condition.review = review
        }
        if(comment_percent){
            condition.comment_percent = comment_percent
        }
        if(buyer_number){
            condition.buyer_number = buyer_number
        }
        if(buyer_phone){
            condition.buyer_phone = buyer_phone
        }
        if(buyer_email){
            condition.buyer_email = buyer_email
        }
        if(member_expiry_time){
            condition.member_expiry_time = member_expiry_time
        }
        if(order_first_time){
            condition.order_first_time = order_first_time
        }
        if(site){
            condition.site = site
        }
        if(comment_last_time){
            condition.comment_last_time = comment_last_time
        }
        // console.log(condition);
        tableObj.reload({
            where: {                        //设定异步数据接口的额外参数，任意设
                'condition': JSON.stringify(condition),
            }
            ,page: {
                curr: 1                     //重新从第 1 页开始
            }
        });
        return false;
    });

    // 监听提交,编辑买家信息
    myForm.on('submit(editSave)', function(data){
        // layer.alert(JSON.stringify(data.field), {
        //     title: '最终的提交信息'
        // });
        var id = $("#editInfo").attr('edit-id');
        if(!id){
            layer.msg("编辑失败，无此条记录", {icon: 2});
            return false
        }
        csrftoken();
        $.ajax({
            url: '/backend/buyers/edit/' + id,
            type: 'POST',
            dataType: 'JSON',
            data: JSON.stringify(data.field),
            success:function (arg) {
                if(arg.code == 0){
                    layer.closeAll();
                    layer.msg('编辑成功', {icon:1});
                    tableObj.reload();
                }else {
                    layer.msg(arg.msg, {icon: 2})
                }
            },
            error :function (arg) {
                 //get the status code
                if (arg.status == 403) {
                    layer.msg(arg.responseText, {icon: 2})
                } else {
                    layer.msg('编辑失败', {icon: 2});
                }
            }
        });

        return false;
    });

    $("#cancelEdit").click(function () {
        layer.closeAll();
        // 清空编辑表单的值
        document.getElementById("editInfo").reset();
    });

    $("#buyerExport").click(function () {
        var d = {};
        var t = $('.form-search').serializeArray();
        $.each(t, function() {
            d[this.name] = this.value;
        });

        if(!d['platform']){
            delete d['platform']
        }
        if(!d['buyer_status']){
            delete d['buyer_status']
        }
        if(!d['cc']){
            delete d['cc']
        }
        if(!d['order_vaild']){
            delete d['order_vaild']
        }
        if(!d['site']){
            delete d['site']
        }
        if(!d['member_type']){
            delete d['member_type']
        }
        if(!d['review']){
            delete d['review']
        }
        if(!d['comment_percent']){
            delete d['comment_percent']
        }
        if(!d['buyer_number']){
            delete d['buyer_number']
        }
        if(!d['buyer_phone']){
            delete d['buyer_phone']
        }
        if(!d['buyer_email']){
            delete d['buyer_email']
        }
        if(!d['member_expiry_time']){
            delete d['member_expiry_time']
        }
        if(!d['order_first_time']){
            delete d['order_first_time']
        }
        if(!d['comment_last_time']){
            delete d['comment_last_time']
        }
        // alert(JSON.stringify(d));

        const url = '/backend/buyers/export/?params=' + JSON.stringify(d);
        const link = document.createElement('a');
        link.style.display = 'none';
        link.href = url;
        link.setAttribute(
          'download',
          "买家名单"
        );
        document.body.appendChild(link);
        link.click();
    });

    $("#buyerImport").click(function () {
        $('#excelHandler').find('input').remove();
        $('#excelHandler').html('<input style="display: none" type="file" id="buyerImportReal">');
        $('#excelHandler').find('#buyerImportReal').click();
        var $input = $("#buyerImportReal");
        $input.change(function () {
            if($(this).val() != ""){
                var arry_name = $("#buyerImportReal")[0].files[0].name.split(".");
                var layout = arry_name.length - 1;
                if(arry_name[layout] != "xlsx"){    // 获取上传格式
                    layer.msg("导入失败，表格必须为xlsx格式")
                }
                // else if($("#complayBill")[0].files[0].size > 1048576){
                //     layer.msg("文件大小必须小于1M")
                // }
                else {
                    var indexLoad = layer.load();
                    var url = "/backend/buyers/import/";
                    // ④创建一个formData对象
                    var formData = new FormData();
                    //⑤获取传入元素的val
                    var name = $(this).val();
                      //⑥获取files
                    var files = $(this)[0].files[0];
                    //⑦将name 和 files 添加到formData中，键值对形式
                    formData.append("file", files);
                    formData.append("name", name);
                    csrftoken();
                    $.ajax({
                        url: url,
                        type: 'POST',
                        data: formData,
                        processData: false,// ⑧告诉jQuery不要去处理发送的数据
                        contentType: false, // ⑨告诉jQuery不要去设置Content-Type请求头
                        success: function (arg) {
                            // console.log(arg)
                            if(arg.status == 200){
                                layer.close(indexLoad);
                                layer.msg(arg.msg, {icon: 1});
                                $(this).val('');
                                tableObj.reload();
                            }else {
                                layer.close(indexLoad);
                                layer.msg(arg.msg, {icon: 2});
                                $(this).val('');
                            }
                        },
                        error : function (responseStr) {
                            //12出错后的动作
                            layer.close(indexLoad);
                            layer.alert("上传失败", {icon: 2});
                            $(this).val('');
                        }
                    });
                }
            }
        });
    });

    function searchSelect() {
        $.ajax({
            url: '/backend/buyers/get/search/select/',
            type: 'GET',
            dataType: 'JSON',
            success: function (arg) {
                if(arg.status == 200){
                    // console.log(arg);
                    $.each(arg.platform, function (index, item) {
                        var option = "<option value='"+ item.platform +"'>"+ item.platform +"</option>";
                        $("#platform").append(option)
                    });
                    $.each(arg.member_type, function (index, item) {
                        var option = "<option value='"+ item.member_type +"'>"+ item.member_type +"</option>";
                        $("#memberType").append(option)
                    });
                    $.each(arg.buyer_site_list, function (index, item) {
                        var option = "<option value='"+ item.buyer_site +"'>"+ item.buyer_site +"</option>";
                        $("#buyerSite").append(option)
                    });
                    myForm.render('select');
                }
            }
        })
    }

    function isMobile() {
        var userAgentInfo = navigator.userAgent;

        var mobileAgents = [ "Android", "iPhone", "SymbianOS", "Windows Phone", "iPad","iPod"];

        var mobile_flag = false;

        //根据userAgent判断是否是手机
        for (var v = 0; v < mobileAgents.length; v++) {
            if (userAgentInfo.indexOf(mobileAgents[v]) > 0) {
                mobile_flag = true;
                break;
            }
        }
         var screen_width = window.screen.width;
         var screen_height = window.screen.height;

         //根据屏幕分辨率判断是否是手机
         if(screen_width < 500 && screen_height < 800){
             mobile_flag = true;
         }

         return mobile_flag;
    }
});
