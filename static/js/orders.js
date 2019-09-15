$(function () {
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

    layui.use(['element', 'table', 'form', 'jquery', 'laydate'], function() {
        var element = layui.element,
        table = layui.table,
        $ = layui.jquery,
        myForm = layui.form;
        laydate = layui.laydate;

        var mobile_flag = isMobile();

        //日期范围
        laydate.render({
            elem: '#order_time'
            ,format: 'MM/dd/yyyy'
            ,range: '~'
        });
        laydate.render({
            elem: '#review_time'
            ,format: 'MM/dd/yyyy'
            ,range: '~'
        });
        laydate.render({
            elem: '#fb_time'
            ,format: 'MM/dd/yyyy'
            ,range: '~'
        });

        var tableObj = table.render({
            elem: '#tbOrders'
            ,url: '/backend/orders/view/'
            ,cellMinWidth: 80
            ,page: true                                    //开启分页
            ,limit: 20
            ,limits: [10,20,30]
            ,defaultToolbar: []
            ,cols: [[
                {type: 'checkbox', width: 50}
                ,{field:'index', title: '序号', type: 'numbers', width: 50}
                ,{field:'buyer_number', title: '买家编号', width: 100, templet: function (d) {
                        return  '<a name="redirect" href="/backend/orders/edit/detail/'+ d.id +'" class="layui-table-link">'+ d.buyer_number +'</a>'
                }}
                ,{field:'platform', title: '平台', width: 100}
                ,{field:'site', title: '站点', width: 100}
                ,{field:'manager', title: '操作员', width: 100}

                ,{field:'buyer_status', title: '买家状态', width: 100}              // 1
                ,{field:'member_type', title: '会员类别', width: 100}               // 1
                ,{field:'buyer_phone', title: '注册手机', width: 100}               // 1
                ,{field:'buyer_email', title: '注册邮箱', width: 100}               // 1

                ,{field:'order_number', title: '订单号'}
                ,{field:'target_asin', title: '目标ASIN', width: 100}
                ,{field:'store_id', title: '店铺ID'}
                ,{field:'link_asin', title: '关联ASIN', width: 100}
                ,{field:'goods_price', title: '产品单价', width: 100}
                ,{field:'purchase_price', title: '购买金额'}
                ,{field:'order_discount', title: '折扣off'}
                ,{field:'review_status', title: 'Review状态', width: 110}
                ,{field:'feedback_status', title: 'Facebook状态', width: 110}
                ,{field:'order_time', title: '订单时间', width: 120}
                ,{field:'review_time', title: 'Review时间', width: 120}
                ,{field:'feedback_time', title: 'FB时间', width: 120}
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
                            elem: '#e_review_time'
                            ,format: 'MM/dd/yyyy'
                        });
                        laydate.render({
                            elem: '#e_feedback_time'
                            ,format: 'MM/dd/yyyy'
                        });
                        laydate.render({
                            elem: '#e_order_time'
                            ,format: 'MM/dd/yyyy'
                        });

                        laydate.render({
                           elem: '#e_review_time'
                           ,value: data.review_time
                        });
                        laydate.render({
                           elem: '#e_feedback_time'
                           ,value: data.feedback_time
                        });
                        laydate.render({
                           elem: '#e_order_time'
                           ,value: data.order_time
                        });

                        myForm.val('editForm', {
                            buyer_number: data.buyer_number,
                            platform: data.platform,
                            site: data.site,
                            manager: data.manager,
                            order_number: data.order_number,
                            target_asin: data.target_asin,
                            store_id: data.store_id,
                            link_asin: data.link_asin,
                            goods_price: data.goods_price,
                            purchase_price: data.purchase_price,
                            review_status: data.review_status,
                            feedback_status: data.feedback_status,
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
                        url:'/backend/orders/delete/' + data.id,
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

        searchSelect();     // 筛选 平台下拉框

        // 监听提交筛选
        myForm.on('submit(sreachBtn)', function(data){
            // layer.alert(JSON.stringify(data.field), {
            //     title: '最终的提交信息'
            // });
            var platform = data.field.platform;
            var site = data.field.site;
            var manager = data.field.manager;
            var buyer_email = data.field.buyer_email;
            var buyer_number = data.field.buyer_number;
            var buyer_phone = data.field.buyer_phone;
            var target_asin = data.field.target_asin;
            var store_id = data.field.store_id;
            var order_discount = data.field.order_discount;
            var purchase_price = data.field.purchase_price;
            var review_status = data.field.review_status;
            var facebook_status = data.field.facebook_status;
            var order_status = data.field.order_status;
            var buyer_status = data.field.buyer_status;
            var member_type = data.field.member_type;

            var feedback_time = data.field.feedback_time;
            var review_time = data.field.review_time;
            var order_time = data.field.order_time;

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
            if(manager){
                condition.manager = manager
            }
            if(target_asin){
                condition.target_asin = target_asin
            }
            if(member_type){
                condition.member_type = member_type
            }
            if(review_time){
                condition.review_time = review_time
            }
            if(store_id){
                condition.store_id = store_id
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
            if(order_discount){
                condition.order_discount = order_discount
            }
            if(review_status){
                condition.review_status = review_status
            }
            if(purchase_price){
                condition.purchase_price = purchase_price
            }
            if(facebook_status){
                condition.facebook_status = facebook_status
            }
            if(order_status){
                condition.order_status = order_status
            }
            if(feedback_time){
                condition.feedback_time = feedback_time
            }
            if(order_time){
                condition.order_time = order_time
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

        $("#orderImport").click(function () {
            $('#excelHandler').find('input').remove();
            $('#excelHandler').html('<input style="display: none" type="file" id="OrderImportReal">');
            $('#excelHandler').find('#OrderImportReal').click();
            var $input = $("#OrderImportReal");
            $input.change(function () {
                if($(this).val() != ""){
                    var arry_name = $("#OrderImportReal")[0].files[0].name.split(".");
                    var layout = arry_name.length - 1;
                    if(arry_name[layout] != "xlsx"){    // 获取上传格式
                        layer.msg("导入失败，表格必须为xlsx格式")
                    }
                    // else if($("#complayBill")[0].files[0].size > 1048576){
                    //     layer.msg("文件大小必须小于1M")
                    // }
                    else {
                        var indexLoad = layer.load();
                        var url = "/backend/orders/import/";
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

        $("#orderExport").click(function () {
            var d = {};
            var t = $('.form-search').serializeArray();
            $.each(t, function() {
                d[this.name] = this.value;
            });

            if(!d['platform']){
                delete d['platform']
            }
            if(!d['buyer_number']){
                delete d['buyer_number']
            }
            if(!d['site']){
                delete d['site']
            }
            if(!d['manager']){
                delete d['manager']
            }
            if(!d['member_type']){
                delete d['member_type']
            }
            if(!d['buyer_status']){
                delete d['buyer_status']
            }
            if(!d['order_status']){
                delete d['order_status']
            }
            if(!d['review_status']){
                delete d['review_status']
            }
            if(!d['facebook_status']){
                delete d['facebook_status']
            }
            if(!d['purchase_price']){
                delete d['purchase_price']
            }
            if(!d['order_discount']){
                delete d['order_discount']
            }
            if(!d['store_id']){
                delete d['store_id']
            }
            if(!d['buyer_phone']){
                delete d['buyer_phone']
            }
            if(!d['buyer_email']){
                delete d['buyer_email']
            }
            if(!d['target_asin']){
                delete d['target_asin']
            }
            if(!d['order_time']){
                delete d['order_time']
            }
            if(!d['review_time']){
                delete d['review_time']
            }
            if(!d['feedback_time']){
                delete d['feedback_time']
            }
            // alert(JSON.stringify(d));

            const url = '/backend/orders/export/?params=' + JSON.stringify(d);
            const link = document.createElement('a');
            link.style.display = 'none';
            link.href = url;
            link.setAttribute(
              'download',
              "订单表"
            );
            document.body.appendChild(link);
            link.click();
        });

        $("#cancelEdit").click(function () {
            layer.closeAll();
            // 清空编辑表单的值
            document.getElementById("editInfo").reset();
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
                url: '/backend/orders/edit/' + id,
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

        function searchSelect() {
            $.ajax({
                url: '/backend/orders/get/search/select/',
                type: 'GET',
                dataType: 'JSON',
                success: function (arg) {
                    if(arg.status == 200){
                        // console.log(arg);
                        $.each(arg.platform, function (index, item) {
                            var option = "<option value='"+ item.platform +"'>"+ item.platform +"</option>";
                            $("#platform").append(option)
                        });
                        myForm.render('select');
                    }
                }
            })
        }
    })
});
