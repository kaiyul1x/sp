$(function () {
    $('input').blur(function () {
        $(this).removeClass('is-invalid')
        $(this).parent().find('.invalid-feedback').remove()
    })
    $('button[name="get-post"]').click(getPostInfo)
    $('button[name="create-task"]').click(createTask)
    $('button[name="dis-task"]').click(disTask)

    function errHandle(xhr) {
        var responseJSON = xhr.responseJSON
        var status = xhr.status
        if (status === 400) {
            for (key in responseJSON) {
                var e = $(`#${key}`)
                e.addClass('is-invalid')
                e.after(`<div class="invalid-feedback">${responseJSON[key]}</div>`)
            }
        } else {
            alert(responseJSON['detail'])
        }
    }

    function disTask() {
        var taskId = $('#task_id').val()
        if (!taskId) {
            return
        }
        $.ajax({
            url: `/api/v1/jianshu/task/${taskId}/`,
            type: 'DELETE',
            success: function (resp, textStatus, xhr) {
                console.log(resp)
                console.log(textStatus)
                console.log(xhr)
            },
            error: function (xhr, status, error) {
                console.log(xhr)
                console.log(error)
                errHandle(xhr)
            }
        })
    }

    function refreshInfo() {
        var postNum = $('#post_num').val()

        $.ajax({
            url: `/api/v1/jianshu/post/${postNum}/`,
            type: 'GET',
            success: function (resp, textStatus, xhr) {
                $('.post-info:eq(0)').html(`<p>标题：${resp['title']}</br>作者：${resp['author']}</br>浏览量：<span id="views-count">${resp['views_count']}</span></p>`)
            },
            error: function (xhr, status, error) {
                console.log(xhr)
                console.log(error)
                errHandle(xhr)
            }
        })

    }

    function getPostInfo() {
        var postNum = $('#post_num').val()
        if (!postNum) {
            return
        }
        $.ajax({
            url: `/api/v1/jianshu/post/${postNum}/`,
            type: 'GET',
            success: function (resp, textStatus, xhr) {
                console.log(resp)
                console.log(textStatus)
                console.log(xhr)
                $('.post-num-form:eq(0)').hide()
                $('.post-info:eq(0)').html(`<p>标题：${resp['title']}</br>作者：${resp['author']}</br>浏览量：<span id="views-count">${resp['views_count']}</span></p>`)
                $('#csrf_token').val(resp['csrf_token'])
                $('#uuid').val(resp['uuid'])
                $('.increase-views-form:eq(0)').show()
            },
            error: function (xhr, status, error) {
                console.log(xhr)
                console.log(error)
                errHandle(xhr)
            }
        })
    }

    function createTask() {
        var postNum = $('#post_num').val()
        var increaseCount = $('#increase_count').val()
        var csrfToken = $('#csrf_token').val()
        var uuid = $('#uuid').val()
        if (postNum && increaseCount && csrfToken && uuid) {
            $.ajax({
                url: `/api/v1/jianshu/task/`,
                type: 'POST',
                data: {
                    'increase_count': increaseCount,
                    'post_num': postNum,
                    'csrf_token': csrfToken,
                    'uuid': uuid
                },
                success: function (resp, textStatus, xhr) {
                    console.log(resp)
                    console.log(xhr)
                    if (xhr.status === 200) {
                        alert('已经有一个任务正在进行。将显示该任务进度')
                    }

                    $('.increase-views-form:eq(0)').hide()
                    $('.progress-div:eq(0)').show()
                    $('#task_id').val(resp['task_id'])
                    var loc = window.location
                    var wsStart = 'ws://'
                    if (loc.protocol == 'https:') {
                        wsStart = 'wss://'
                    }
                    var endpoint = wsStart + loc.host + `/ws/task/progress/${resp['task_id']}/`
                    var socket = new WebSocket(endpoint)
                    var timer = setInterval(refreshInfo, 2000)
                    socket.onmessage = function (e) {
                        console.log('message', e)
                        var dataJSON = JSON.parse(e['data'])
                        console.log(dataJSON)

                        var content = JSON.parse(dataJSON['content'])
                        var status = content['status']
                        var progress = new Decimal(Math.round(content['progress'] * 1000) / 1000).mul(new Decimal(100)).toNumber()

                        console.log(progress)
                        var progressBar = $('.progress .progress-bar')
                        progressBar.attr('style', `width: ${progress}%`)
                        progressBar.attr('aria-valuenow', `${progress}`)
                        progressBar.html(`${progress}%`)

                        if (status === 'FINISH') {
                            clearInterval(timer)
                            refreshInfo()
                            setTimeout(function () {
                                alert('完成')
                                $('.progress-div:eq(0)').hide()
                                $('.increase-views-form:eq(0)').show()
                                progressBar.attr('style', `width: 0%`)
                                progressBar.attr('aria-valuenow', `0`)
                                progressBar.html(`0%`)
                            }, 500);
                            return
                        } else if (status === 'FAIL') {
                            clearInterval(timer)
                            refreshInfo()
                            alert('失败')
                            $('.progress-div:eq(0)').hide()
                            $('.increase-views-form:eq(0)').show()
                            progressBar.attr('style', `width: 0%`)
                            progressBar.attr('aria-valuenow', `0`)
                            progressBar.html(`0%`)
                            return
                        } else if (status === 'CANCEL') {
                            clearInterval(timer)
                            refreshInfo()
                            alert('任务取消')
                            $('.progress-div:eq(0)').hide()
                            $('.increase-views-form:eq(0)').show()
                            progressBar.attr('style', `width: 0%`)
                            progressBar.attr('aria-valuenow', `0`)
                            progressBar.html(`0%`)
                            return
                        }
                    }
                    socket.onopen = function (e) {
                        console.log('onopen', e)
                    }
                    socket.onerror = function (e) {
                        console.log('onerror', e)
                    }
                    socket.onclose = function (e) {
                        console.log('onclose', e)
                    }

                },
                error: function (xhr, status, error) {
                    console.log(xhr)
                    console.log(error)
                    errHandle(xhr)
                }
            })
        }
    }
})
