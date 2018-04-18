var map = []
var jc=null
var actionSocket = io.connect("http://" + window.location.host + '/action');
Array.prototype.indexOf = function(val) {
    for (var i = 0; i < this.length; i++) {
        if (this[i] == val) return i
    }
    return -1
}
Array.prototype.remove=function(val){
	var index=this.indexOf(val);
	if (index>-1){
		this.splice(index,1);
	}
}
//获取可用设备列表
function getDeviceList(ele) {
    eleid = $(ele).parent().parent().attr('id')
    url = "http://" + window.location.host + '/testcase/getDeviceList?eleid=' + eleid
    jc = $.confirm({
        content: 'url:' + url,
        columnClass: 'col-md-12',
        title: 'Avaliable Devices',
        animation: 'top',
        cancelButton: false,
        confirmButton: false,
    })
}
//切换view
function getloadderView(eleid) {
    $('#' + eleid).find('#initView').hide()
    $('#' + eleid).find('#myloadder').show()

}
function errorView(eleid,data) {
	console.log(data,eleid)
    errorJc = $.confirm({
        content: data.name+':'+data.data,
        columnClass: 'col-md-12',
        title: 'FuckError2',
        animation: 'top',
        cancelButton: false,
        confirmButton: false,
    })	
}
function getinitView(eleid) {
    $('#' + eleid).trigger('offsc')
    $('#' + eleid).find('#panel').hide()
    $('#' + eleid).find('#initView').show()
    $('#' + eleid).find('#devicename').removeAttr('abc')
    $('#' + eleid).find('#devicename').attr('class','devicename-off')
    var serial = $('#' + eleid).find('#devicename').attr('abc')
    map.remove(serial)
}

function getdeviceView(eleid) {
    $('#' + eleid).find('#myloadder').hide()
    $('#' + eleid).find('#panel').show()

}

//添加（注册）一台设备
function addDeviceView(eleid, serial) {
    // panel = $('#' + eleid).find('#panel')
    getloadderView(eleid)

    title = $('#' + eleid).find('#devicename')
    title.attr('abc', serial)
    title.on('click', choiceDevice)

    $.getJSON($SCRIPT_ROOT + 'addDeviceView', { 'serial': serial }, function(data) {
        $('#' + eleid).find('#devicename').text(data.manufacturer)
        registerView(serial, eleid, data)
        getdeviceView(eleid)
    })
    jc.close()
}
//选择同时操作设备
function choiceDevice(serial) {
    if (this.className == 'devicename-on') {
        this.className = 'devicename-off'
    } else {
        this.className = 'devicename-on'
    }
    ddd = $(".devicename-on")
        // console.log(ddd.length)
    map = []
    ddd.each(function() {
            map.push($(this).attr('abc'))
        })
        // if (map.length == 4) {
        //     $('#turn').text('all')
        // } else if (map.length == 0) {
        //     $('#turn').text('clear')
        // }
    console.log(map)
}

//选择所有设备同时操作
function choiceAllDevice() {
    $(".devicename-off").each(function() {

    	if ($(this).attr('abc')){
        this.className = "devicename-on"
   }
    })
    map = []
    ddd = $(".devicename-on")
    ddd.each(function() {
        map.push($(this).attr('abc'))
    })
}
//取消选择所有设备同时操作
function clearAllDevice() {
    $(".devicename-on").each(function() {
        this.className = "devicename-off"
    })
    map = []
}

function removeDeviceView(ele) {
    id = $(ele).parent().parent().parent().parent().attr('id')
    // $('#' + eleid).find('#devicename').attr('abc', '')
    console.log(id)
    getinitView(id)
        // $(ele).parent().show()

    // $('#device1').show()
    // alert(id)
    // $.getJSON($SCRIPT_ROOT+'getDeviceStatus',{'serial':'fa3fb4067d52'},function(data){

    // })
}

// Util
function VendorUtilFactory() {
    var vendorUtil = {}

    vendorUtil.style = function(props) {
        var testee = document.createElement('span')
        for (var i = 0, l = props.length; i < l; ++i) {
            if (typeof testee.style[props[i]] !== 'undefined') {
                return props[i]
            }
        }
        return props[0]
    }

    return vendorUtil
}

function ScalingServiceFactory() {
    var scalingService = {}
    scalingService.coordinator = function(realWidth, realHeight) {
        var realRatio = realWidth / realHeight
        return {
            coords: function(boundingW, boundingH, relX, relY, rotation) {
                var w, h, x, y, ratio, scaledValue

                switch (rotation) {
                    case 0:
                        w = boundingW
                        h = boundingH
                        x = relX
                        y = relY
                        break
                    case 90:
                        w = boundingH
                        h = boundingW
                        x = boundingH - relY
                        y = relX
                        break
                    case 180:
                        w = boundingW
                        h = boundingH
                        x = boundingW - relX
                        y = boundingH - relY
                        break
                    case 270:
                        w = boundingH
                        h = boundingW
                        x = relY
                        y = boundingW - relX
                        break
                }

                ratio = w / h

                if (realRatio > ratio) {
                    // covers the area horizontally
                    scaledValue = w / realRatio

                    // adjust y to start from the scaled top edge
                    y -= (h - scaledValue) / 2

                    // not touching the screen, but we want to trigger certain events
                    // (like touchup) anyway, so let's do it on the edges.
                    if (y < 0) {
                        y = 0
                    } else if (y > scaledValue) {
                        y = scaledValue
                    }

                    // make sure x is within bounds too
                    if (x < 0) {
                        x = 0
                    } else if (x > w) {
                        x = w
                    }

                    h = scaledValue
                } else {
                    // covers the area vertically
                    scaledValue = h * realRatio

                    // adjust x to start from the scaled left edge
                    x -= (w - scaledValue) / 2

                    // not touching the screen, but we want to trigger certain events
                    // (like touchup) anyway, so let's do it on the edges.
                    if (x < 0) {
                        x = 0
                    } else if (x > scaledValue) {
                        x = scaledValue
                    }

                    // make sure y is within bounds too
                    if (y < 0) {
                        y = 0
                    } else if (y > h) {
                        y = h
                    }

                    w = scaledValue
                }

                return {
                    xP: x / w,
                    yP: y / h
                }
            },
            size: function(sizeWidth, sizeHeight) {
                var width = sizeWidth
                var height = sizeHeight
                var ratio = width / height

                if (realRatio > ratio) {
                    // covers the area horizontally

                    if (width >= realWidth) {
                        // don't go over max size
                        width = realWidth
                        height = realHeight
                    } else {
                        height = Math.floor(width / realRatio)
                    }
                } else {
                    // covers the area vertically

                    if (height >= realHeight) {
                        // don't go over max size
                        height = realHeight
                        width = realWidth
                    } else {
                        width = Math.floor(height * realRatio)
                    }
                }

                return {
                    width: width,
                    height: height
                }
            },
            projectedSize: function(boundingW, boundingH, rotation) {
                var w, h

                switch (rotation) {
                    case 0:
                    case 180:
                        w = boundingW
                        h = boundingH
                        break
                    case 90:
                    case 270:
                        w = boundingH
                        h = boundingW
                        break
                }

                var ratio = w / h

                if (realRatio > ratio) {
                    // covers the area horizontally
                    h = Math.floor(w / realRatio)
                } else {
                    w = Math.floor(h * realRatio)
                }

                return {
                    width: w,
                    height: h
                }
            }
        }
    }
    return scalingService
}
var mapping = {
    0: { 0: 0, 90: -90, 180: -180, 270: 90 },
    90: { 0: 90, 90: 0, 180: -90, 270: 180 },
    180: { 0: 180, 90: 90, 180: 0, 270: -90 },
    270: { 0: -90, 90: -180, 180: 90, 270: 0 }
}

function registerView(serial, eleid, infos) {

    var panel = $('#' + eleid).find('#panel')
    var element = panel.find('#hahaha')
    var $document = $(document)
    var device = { 'display': { 'rotation': infos.display.rotation, 'width': infos.display.width, 'height': infos.display.height } }
    var BLANK_IMG = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    var input = element.find('input')
    var screen = { rotation: 0, bounds: { x: 0, y: 0, w: 0, h: 0 } }
    var cssTransform = VendorUtilFactory().style(['transform', 'webkitTransform'])
    var scaler = ScalingServiceFactory().coordinator(device.display.width, device.display.height)

    /*
     *
     * SCREEN HANDLING
     *
     */
    ;
    (function() {
        function ImagePool(size) {
            this.size = size
            this.images = []
            this.counter = 0
        }
        ImagePool.prototype.next = function() {
            if (this.images.length < this.size) {
                var image = new Image()
                this.images.push(image)
                return image
            } else {
                if (this.counter >= this.size) {
                    // Reset for unlikely but theoretically possible overflow.
                    this.counter = 0
                }
                return this.images[this.counter++ % this.size]
            }
        }
        $('#' + eleid).on('offsc', function() {
            console.log('get offsc')
            $('#' + eleid).unbind()
            $('#' + eleid).find('#panel').find('#power').off('click')
            g.clearRect(0, 0, canvas.width, canvas.height)
            onScreenInterestLost()
        })

        function disconnectSocket() {
            try {
                screenSocket.removeAllListeners()
                screenSocket.close()
                screenSocket = null
            } catch (err) { console.log('closeError' + err) }
        }
        var screenSocket = io.connect("http://" + window.location.host + '/screen' + serial, { 'forceNew': true });
        screenSocket.binaryType = 'blob'
        var canvas = panel.find('#canvas1')[0]
        var g = canvas.getContext('2d')
        var positioner = element.find('div')[0]
        var devicePixelRatio = window.devicePixelRatio || 1
        var backingStoreRatio = vendorBackingStorePixelRatio(g)
        var frontBackRatio = devicePixelRatio / backingStoreRatio
        var options = { autoScaleForRetina: true, density: Math.max(1, Math.min(1.5, devicePixelRatio || 1)), minscale: 0.36 }

        function vendorBackingStorePixelRatio(g) {
            return g.webkitBackingStorePixelRatio ||
                g.mozBackingStorePixelRatio ||
                g.msBackingStorePixelRatio ||
                g.oBackingStorePixelRatio ||
                g.backingStorePixelRatio || 1
        }
        var adjustedBoundSize
        var cachedEnabled = false

        function updateBounds() {
            // console.log('updatebound')

            function adjustBoundedSize(w, h) {
                var sw = w * options.density
                var sh = h * options.density
                var f

                if (sw < (f = device.display.width * options.minscale)) {
                    sw *= f / sw
                    sh *= f / sh
                }

                if (sh < (f = device.display.height * options.minscale)) {
                    sw *= f / sw
                    sh *= f / sh
                }

                return {
                    w: Math.ceil(sw),
                    h: Math.ceil(sh)
                }
            }

            var w = screen.bounds.w = element[0].offsetWidth
            var h = screen.bounds.h = element[0].offsetHeight
            if (!w || !h) {
                throw new Error(
                    'Unable to read bounds; container must have dimensions'
                )
            }
            var newAdjustedBoundSize = (function() {
                switch (screen.rotation) {
                    case 90:
                    case 270:
                        return adjustBoundedSize(h, w)
                    case 0:
                    case 180:
                        /* falls through */
                    default:
                        return adjustBoundedSize(w, h)
                }
            })()

            if (!adjustedBoundSize ||
                newAdjustedBoundSize.w !== adjustedBoundSize.w ||
                newAdjustedBoundSize.h !== adjustedBoundSize.h) {
                adjustedBoundSize = newAdjustedBoundSize
                onScreenInterestAreaChanged()
            }
        }

        function shouldUpdateScreen() {

            return (
                screenSocket.connected
                // NO if the user has disabled the screen.
                // scope.$parent.showScreen &&
                // // NO if we're not even using the device anymore.
                // device.using &&
                // // NO if the page is not visible (e.g. background tab).
                // !PageVisibilityService.hidden &&
                // // // NO if we don't have a connection yet.
                // ws.readyState === WebSocket.OPEN
                // // YES otherwise
            )
        }

        function checkEnabled() {
            var newEnabled = shouldUpdateScreen()
            if (newEnabled === cachedEnabled) {
                updateBounds()
            } else if (newEnabled) {
                updateBounds()
                onScreenInterestGained()
            } else {
                g.clearRect(0, 0, canvas.width, canvas.height)
                onScreenInterestLost()
            }

            cachedEnabled = newEnabled
        }

        function onScreenInterestGained() {
            console.log('start', screenSocket.connected, screenSocket)
            actionSocket.emit('size', { 'x': adjustedBoundSize.w, 'y': adjustedBoundSize.h, 'serial': serial })
            actionSocket.emit('onscreen', { 'serial': serial })
        }


        function onScreenInterestAreaChanged() {
            actionSocket.emit('size', { 'x': adjustedBoundSize.w, 'y': adjustedBoundSize.h, 'serial': serial })
            console.log('changesize')
        }

        function onScreenInterestLost() {
            actionSocket.emit('offscreen', { 'serial': serial })

            // stopabc()
            console.log('stop')
        }
        actionSocket.on('installResponse', function(data) {
            console.log(data)
            if (data.result == 'success') {
                $.danidemo.updateFileProgress(data.id, data.data);
                if (data.data == '90%') {
                    $.danidemo.updateFileStatus(data.id, 'success', 'Install...');
                } else if (data.data == '98%') {
                    $.danidemo.updateFileStatus(data.id, 'success', 'Launch...');
                } else {
                    $.danidemo.updateFileStatus(data.id, 'success', 'Done...');
                    $.danidemo.hideProgress(data.id, data.data)
                    $.danidemo.showDetail('#demo-files', data.packageName, data.activity, data.version)
                }
            } else {
                console.log('hehehe')
                $.danidemo.updateFileStatus(data.id, 'error', data.data);
                // $.danidemo.addLog('#demo-debug', 'error', 'getError#' + data.id + ': ' + data.data);
            }


        })
        function setrotate(rotation) {
            device.display.rotation = rotation
            actionSocket.emit('rotation', { 'rotation': rotation, 'serial': serial })
        }
        screenSocket.on('event', function(data) {
            console.log('getevent')
            console.log(data)
            if (data['eventname'] == 'RotationEvent') {
                setrotate(data['data']['rotation'])
            }
        })
        screenSocket.on('connect', function() {
            checkEnabled()
        })
        screenSocket.on('system', function(data) {
        	// errorView(eleid,data)
            //1208
            console.log('1208')
            // $('#' + data['name']).text(data['data']);
        })
        screenSocket.on('imgdata',
            function(data) {
                var cachedScreen = { rotation: 0, bounds: { x: 0, y: 0, w: 0, h: 0 } }
                var cachedImageWidth = 0
                var cachedImageHeight = 0
                var cssRotation = 0
                var alwaysUpright = true
                var imagePool = new ImagePool(10)

                function hasImageAreaChanged(img) {
                    return cachedScreen.bounds.w !== screen.bounds.w ||
                        cachedScreen.bounds.h !== screen.bounds.h ||
                        cachedImageWidth !== img.width ||
                        cachedImageHeight !== img.height ||
                        cachedScreen.rotation !== screen.rotation
                }

                function isRotated() {
                    // alert('haha',screen.rotation === 90 || screen.rotation === 270)
                    return screen.rotation === 90 || screen.rotation === 270
                }

                function rotator(oldRotation, newRotation) {
                    var r1 = oldRotation < 0 ? 360 + oldRotation % 360 : oldRotation % 360
                    var r2 = newRotation < 0 ? 360 + newRotation % 360 : newRotation % 360

                    return mapping[r1][r2]
                }

                function updateImageArea(img) {
                    // console.log(img.width,img.height)
                    if (!hasImageAreaChanged(img)) {
                        return
                    }

                    cachedImageWidth = img.width
                    cachedImageHeight = img.height

                    if (options.autoScaleForRetina) {
                        canvas.width = cachedImageWidth * frontBackRatio
                        canvas.height = cachedImageHeight * frontBackRatio
                        g.scale(frontBackRatio, frontBackRatio)
                    } else {
                        console.log('yes')
                        canvas.width = cachedImageWidth
                        canvas.height = cachedImageHeight
                    }

                    cssRotation += rotator(cachedScreen.rotation, screen.rotation)
                    canvas.style[cssTransform] = 'rotate(' + cssRotation + 'deg)'
                    console.log('cssRotation', cssRotation, screen.rotation)
                    cachedScreen.bounds.h = screen.bounds.h
                    cachedScreen.bounds.w = screen.bounds.w
                    cachedScreen.rotation = screen.rotation
                    canvasAspect = canvas.width / canvas.height

                    if (isRotated() && !alwaysUpright) {
                        canvasAspect = img.height / img.width
                        element[0].classList.add('rotated')
                    } else {
                        canvasAspect = img.width / img.height
                        element[0].classList.remove('rotated')
                    }

                    if (alwaysUpright) {
                        // If the screen image is always in upright position (but we
                        // still want the rotation animation), we need to cancel out
                        // the rotation by using another rotation.
                        positioner.style[cssTransform] = 'rotate(' + -cssRotation + 'deg)'
                    }
                    maybeFlipLetterbox()

                }

                return function messageListener(data) {
                    // console.log('mess',data)
                    screen.rotation = device.display.rotation
                        // if (data instanceof Blob){
                    if (shouldUpdateScreen()) {
                        // console.log('iamin')
                        var blob = new Blob([data], {
                            type: 'image/jpeg'
                        })

                        var img = imagePool.next()

                        img.onload = function() {
                            updateImageArea(this)

                            g.drawImage(img, 0, 0, img.width, img.height)

                            // Try to forcefully clean everything to get rid of memory
                            // leaks. Note that despite this effort, Chrome will still
                            // leak huge amounts of memory when the developer tools are
                            // open, probably to save the resources for inspection. When
                            // the developer tools are closed no memory is leaked.
                            img.onload = img.onerror = null
                            img.src = BLANK_IMG
                            img = null
                            blob = null

                            URL.revokeObjectURL(url)
                            url = null
                        }

                        img.onerror = function() {
                            // Happily ignore. I suppose this shouldn't happen, but
                            // sometimes it does, presumably when we're loading images
                            // too quickly.

                            // Do the same cleanup here as in onload.
                            img.onload = img.onerror = null
                            img.src = BLANK_IMG
                            img = null
                            blob = null

                            URL.revokeObjectURL(url)
                            url = null
                        }

                        var url = URL.createObjectURL(blob)
                        img.src = url
                    }
                    // }
                }
            }())
        element.on('resize', updateBounds)
        var canvasAspect = 1
        var parentAspect = 1

        function maybeFlipLetterbox() {
            element[0].classList.toggle(
                'letterboxed', parentAspect < canvasAspect)
        }
    })();
      /**
       * KEYBOARD HANDLING
       *
       * This should be moved elsewhere, but due to shared dependencies and
       * elements it's currently here. So basically due to laziness.
       *
       * For now, try to keep the whole section as a separate unit as much
       * as possible.
       */
    (function() {
        function isChangeCharsetKey(e) {
            // Add any special key here for changing charset
            //console.log('e', e)

            // Chrome/Safari/Opera
            if (
                // Mac | Kinesis keyboard | Karabiner | Latin key, Kana key
                e.keyCode === 0 && e.keyIdentifier === 'U+0010' ||

                // Mac | MacBook Pro keyboard | Latin key, Kana key
                e.keyCode === 0 && e.keyIdentifier === 'U+0020' ||

                // Win | Lenovo X230 keyboard | Alt+Latin key
                e.keyCode === 246 && e.keyIdentifier === 'U+00F6' ||

                // Win | Lenovo X230 keyboard | Convert key
                e.keyCode === 28 && e.keyIdentifier === 'U+001C'
            ) {
                return true
            }

            // Firefox
            switch (e.key) {
                case 'Convert': // Windows | Convert key
                case 'Alphanumeric': // Mac | Latin key
                case 'RomanCharacters': // Windows/Mac | Latin key
                case 'KanjiMode': // Windows/Mac | Kana key
                    return true
            }

            return false
        }

        function handleSpecialKeys(e) {
            if (isChangeCharsetKey(e)) {
                e.preventDefault()
                keyPress('switch_charset')
                return true
            }

            return false
        }

        function keydownListener(e) {
            // Prevent tab from switching focus to the next element, we only want
            // that to happen on the device side.
            // console.log(e.keyCode,'down')
            if (e.keyCode === 9) {
                e.preventDefault()
            }
            // if (e.keyCode === 18) {
            //     e.preventDefault()

            //    console.log('fuck18')
            //    return 
            // }
            if (e.keyCode === 20 || e.keyCode === 91) {
                e.preventDefault()
                choiceAllDevice()
                    // return
            }
            keyDown(e.keyCode)
        }

        function keyupListener(e) {
            // console.log(e.keyCode,'up')
            if (e.keyCode === 20 || e.keyCode === 91) {
                // console.log('hehe')
                clearAllDevice()
                    // return
            }
            if (!handleSpecialKeys(e)) {
                keyUp(e.keyCode)
            }
        }

        // function pasteListener(e) {
        //     // Prevent value change or the input event sees it. This way we get
        //     // the real value instead of any "\n" -> " " conversions we might see
        //     // in the input value.
        //     e.preventDefault()
        //     control.paste(e.clipboardData.getData('text/plain'))
        // }

        // function copyListener(e) {
        //     e.preventDefault()
        //         // This is asynchronous and by the time it returns we will no longer
        //         // have access to setData(). In other words it doesn't work. Currently
        //         // what happens is that on the first copy, it will attempt to fetch
        //         // the clipboard contents. Only on the second copy will it actually
        //         // copy that to the clipboard.
        //     control.getClipboardContent()
        //     if (control.clipboardContent) {
        //         e.clipboardData.setData('text/plain', control.clipboardContent)
        //     }
        // }

        function inputListener() {
            // Why use the input event if we don't let it handle pasting? The
            // reason is that on latest Safari (Version 8.0 (10600.1.25)), if
            // you use the "Romaji" Kotoeri input method, we'll never get any
            // keypress events. It also causes us to lose the very first keypress
            // on the page. Currently I'm not sure if we can fix that one.
            type(this.value)
            this.value = ''
        }

        panel.bind('keydown', keydownListener)
        panel.bind('keyup', keyupListener)
        input.bind('input', inputListener)
            // input.bind('paste', pasteListener)
            // input.bind('copy', copyListener)
        $('#' + eleid).on('offsc', function() {
            panel.unbind()
            input.unbind()
        })

        // function setrotate(rotation) {
        //     device.display.rotation = rotation
        //     actionSocket.emit('rotation', { 'rotation': rotation, 'serial': serial })
        // }

        // screenSocket.on('event', function(data) {
        //     console.log('getevent')
        //     console.log(data)
        //     if (data['eventname'] == 'RotationEvent') {
        //         setrotate(data['data']['rotation'])
        //     }
        // })
        actionSocket.on('actionRes', function(data) {
            if (data['result'] == 'error') {
                console.log('abc')
                // alert(data['msg'])//1208
            }
        })

    })()
    KeycodesMapped = {
        "8": "del",
        "9": "tab",
        "13": "enter",
        "20": "caps_lock",
        "27": "escape",
        "33": "page_up",
        "34": "page_down",
        "35": "move_end",
        "36": "move_home",
        "37": "dpad_left",
        "38": "dpad_up",
        "39": "dpad_right",
        "40": "dpad_down",
        "45": "insert",
        "46": "forward_del",
        "93": "menu",
        "112": "f1",
        "113": "f2",
        "114": "f3",
        "115": "f4",
        "116": "f5",
        "117": "f6",
        "118": "f7",
        "119": "f8",
        "120": "f9",
        "121": "f10",
        "122": "f11",
        "123": "f12",
        "144": "num_lock"
    }

    function keySender(type, fixedKey) {
        return function(key) {
            if (typeof key === 'string') {
                console.log('sendt')
                sendOneWay(type, {
                    key: key
                })
            } else {
                var mapped = fixedKey || KeycodesMapped[key]
                if (mapped) {
                    sendOneWay(type, {
                        key: mapped
                    })
                }
            }
        }
    }

    function type(text) {
        console.log('type' + text)
        sendOneWay('type', {
            text: text
        })
        console.log(text)
    }

    function keyDown(key) {
        keySender('keyDown')(key)
    }

    function keyUp(key) {
        keySender('keyUp')(key)
    }

    function keyPress(key) {
        keySender('keyPress')(key)
    }

    function home() {
        keySender('keyPress', 'home')()
    }

    function menu() {
        keySender('keyPress', 'menu')()
    }

    function back() {
        keySender('keyPress', 'back')()
    }

    function wake() {
        sendOneWay('wake', { 'wake': 'wake' })
    }

    function power() {
        keySender('keyPress', 'power')()
    }

    function volumeOff() {
        keySender('keyPress', 'volume_mute')()
    }

    function volumeDown() {
        keySender('keyPress', 'volume_down')()
    }

    function volumeUp() {
        keySender('keyPress', 'volume_up')()
    }
    // touch handler
    ;
    (function() {
        var slots = []
        var slotted = Object.create(null)
        var fingers = []
        var seq = -1
        var cycle = 100
        var fakePinch = false
        var lastPossiblyBuggyMouseUpEvent = 0

        function nextSeq() {
            return ++seq >= cycle ? (seq = 0) : seq
        }

        function createSlots() {
            // The reverse order is important because slots and fingers are in
            // opposite sort order. Anyway don't change anything here unless
            // you understand what it does and why.
            for (var i = 9; i >= 0; --i) {
                var finger = createFinger(i)
                element.append(finger)
                slots.push(i)
                fingers.unshift(finger)
            }
        }

        function activateFinger(index, x, y, pressure) {
            var scale = 0.5 + pressure
            fingers[index].classList.add('active')
            fingers[index].style[cssTransform] =
                'translate3d(' + x + 'px,' + y + 'px,0) ' +
                'scale(' + scale + ',' + scale + ')'
        }

        function deactivateFinger(index) {
            fingers[index].classList.remove('active')
        }

        function deactivateFingers() {
            for (var i = 0, l = fingers.length; i < l; ++i) {
                fingers[i].classList.remove('active')
            }
        }

        function createFinger(index) {
            var el = document.createElement('span')
            el.className = 'finger finger-' + index
            return el
        }

        function calculateBounds() {
            var el = element[0]

            screen.bounds.w = el.offsetWidth
            screen.bounds.h = el.offsetHeight
            screen.bounds.x = 0
            screen.bounds.y = 0

            while (el.offsetParent) {
                screen.bounds.x += el.offsetLeft
                screen.bounds.y += el.offsetTop
                el = el.offsetParent
            }
        }

        function mouseDownListener(event) {
            var e = event
            if (e.originalEvent) {
                e = e.originalEvent
            }

            // Skip secondary click
            if (e.which === 3) {
                return
            }

            e.preventDefault()

            fakePinch = e.altKey

            calculateBounds()
            startMousing()

            var x = e.pageX - screen.bounds.x
            var y = e.pageY - screen.bounds.y
            var pressure = 0.5
            var scaled = scaler.coords(
                screen.bounds.w, screen.bounds.h, x, y, screen.rotation
            )

            touchDown(nextSeq(), 0, scaled.xP, scaled.yP, pressure)

            if (fakePinch) {
                touchDown(nextSeq(), 1, 1 - scaled.xP, 1 - scaled.yP,
                    pressure)
            }

            touchCommit(nextSeq())

            activateFinger(0, x, y, pressure)

            if (fakePinch) {
                activateFinger(1, -e.pageX + screen.bounds.x + screen.bounds.w, -e.pageY + screen.bounds.y + screen.bounds.h, pressure)
            }

            element.bind('mousemove', mouseMoveListener)
            $document.bind('mouseup', mouseUpListener)
            $document.bind('mouseleave', mouseUpListener)

            if (lastPossiblyBuggyMouseUpEvent &&
                lastPossiblyBuggyMouseUpEvent.timeStamp > e.timeStamp) {
                // We got mouseup before mousedown. See mouseUpBugWorkaroundListener
                // for details.
                mouseUpListener(lastPossiblyBuggyMouseUpEvent)
            } else {
                lastPossiblyBuggyMouseUpEvent = null
            }
        }

        function mouseMoveListener(event) {
            var e = event
            if (e.originalEvent) {
                e = e.originalEvent
            }

            // Skip secondary click
            if (e.which === 3) {
                return
            }
            e.preventDefault()

            var addGhostFinger = !fakePinch && e.altKey
            var deleteGhostFinger = fakePinch && !e.altKey

            fakePinch = e.altKey

            var x = e.pageX - screen.bounds.x
            var y = e.pageY - screen.bounds.y
            var pressure = 0.5
            var scaled = scaler.coords(
                screen.bounds.w, screen.bounds.h, x, y, screen.rotation
            )

            touchMove(nextSeq(), 0, scaled.xP, scaled.yP, pressure)

            if (addGhostFinger) {
                touchDown(nextSeq(), 1, 1 - scaled.xP, 1 - scaled.yP, pressure)
            } else if (deleteGhostFinger) {
                touchUp(nextSeq(), 1)
            } else if (fakePinch) {
                touchMove(nextSeq(), 1, 1 - scaled.xP, 1 - scaled.yP, pressure)
            }

            touchCommit(nextSeq())

            activateFinger(0, x, y, pressure)

            if (deleteGhostFinger) {
                deactivateFinger(1)
            } else if (fakePinch) {
                activateFinger(1, -e.pageX + screen.bounds.x + screen.bounds.w, -e.pageY + screen.bounds.y + screen.bounds.h, pressure)
            }
        }

        function mouseUpListener(event) {
            var e = event
            if (e.originalEvent) {
                e = e.originalEvent
            }

            // Skip secondary click
            if (e.which === 3) {
                return
            }
            e.preventDefault()

            touchUp(nextSeq(), 0)

            if (fakePinch) {
                touchUp(nextSeq(), 1)
            }

            touchCommit(nextSeq())

            deactivateFinger(0)

            if (fakePinch) {
                deactivateFinger(1)
            }

            stopMousing()
        }

        /**
         * Do NOT remove under any circumstances. Currently, in the latest
         * Safari (Version 8.0 (10600.1.25)), if an input field is focused
         * while we do a tap click on an MBP trackpad ("Tap to click" in
         * Settings), it sometimes causes the mouseup event to trigger before
         * the mousedown event (but event.timeStamp will be correct). It
         * doesn't happen in any other browser. The following minimal test
         * case triggers the same behavior (although less frequently). Keep
         * tapping and you'll eventually see see two mouseups in a row with
         * the same counter value followed by a mousedown with a new counter
         * value. Also, when the bug happens, the cursor in the input field
         * stops blinking. It may take up to 300 attempts to spot the bug on
         * a MacBook Pro (Retina, 15-inch, Mid 2014).
         *
         *     <!doctype html>
         *
         *     <div id="touchable"
         *       style="width: 100px; height: 100px; background: green"></div>
         *     <input id="focusable" type="text" />
         *
         *     <script>
         *     var touchable = document.getElementById('touchable')
         *       , focusable = document.getElementById('focusable')
         *       , counter = 0
         *
         *     function mousedownListener(e) {
         *       counter += 1
         *       console.log('mousedown', counter, e, e.timeStamp)
         *       e.preventDefault()
         *     }
         *
         *     function mouseupListener(e) {
         *       e.preventDefault()
         *       console.log('mouseup', counter, e, e.timeStamp)
         *       focusable.focus()
         *     }
         *
         *     touchable.addEventListener('mousedown', mousedownListener, false)
         *     touchable.addEventListener('mouseup', mouseupListener, false)
         *     </script>
         *
         * I believe that the bug is caused by some kind of a race condition
         * in Safari. Using a textarea or a focused contenteditable does not
         * get rid of the bug. The bug also happens if the text field is
         * focused manually by the user (not with .focus()).
         *
         * It also doesn't help if you .blur() before .focus().
         *
         * So basically we'll just have to store the event on mouseup and check
         * if we should do the browser's job in the mousedown handler.
         */
        function mouseUpBugWorkaroundListener(e) {
            lastPossiblyBuggyMouseUpEvent = e
        }

        function startMousing() {
            gestureStart(nextSeq())
            input[0].focus()
        }

        function stopMousing() {
            element.unbind('mousemove', mouseMoveListener)
            $document.unbind('mouseup', mouseUpListener)
            $document.unbind('mouseleave', mouseUpListener)
            deactivateFingers()
            gestureStop(nextSeq())
        }

        function touchStartListener(event) {
            var e = event
            e.preventDefault()

            //Make it jQuery compatible also
            if (e.originalEvent) {
                e = e.originalEvent
            }

            calculateBounds()

            if (e.touches.length === e.changedTouches.length) {
                startTouching()
            }

            var currentTouches = Object.create(null)
            var i, l

            for (i = 0, l = e.touches.length; i < l; ++i) {
                currentTouches[e.touches[i].identifier] = 1
            }

            function maybeLostTouchEnd(id) {
                return !(id in currentTouches)
            }

            // We might have lost a touchend event due to various edge cases
            // (literally) such as dragging from the bottom of the screen so that
            // the control center appears. If so, let's ask for a reset.
            if (Object.keys(slotted).some(maybeLostTouchEnd)) {
                Object.keys(slotted).forEach(function(id) {
                    slots.push(slotted[id])
                    delete slotted[id]
                })
                slots.sort().reverse()
                touchReset(nextSeq())
                deactivateFingers()
            }

            if (!slots.length) {
                // This should never happen but who knows...
                throw new Error('Ran out of multitouch slots')
            }

            for (i = 0, l = e.changedTouches.length; i < l; ++i) {
                var touch = e.changedTouches[i]
                var slot = slots.pop()
                var x = touch.pageX - screen.bounds.x
                var y = touch.pageY - screen.bounds.y
                var pressure = touch.force || 0.5
                var scaled = scaler.coords(
                    screen.bounds.w, screen.bounds.h, x, y, screen.rotation
                )

                slotted[touch.identifier] = slot
                touchDown(nextSeq(), slot, scaled.xP, scaled.yP, pressure)
                activateFinger(slot, x, y, pressure)
            }

            element.bind('touchmove', touchMoveListener)
            $document.bind('touchend', touchEndListener)
            $document.bind('touchleave', touchEndListener)

            touchCommit(nextSeq())
        }

        function touchMoveListener(event) {
            var e = event
            e.preventDefault()

            if (e.originalEvent) {
                e = e.originalEvent
            }

            for (var i = 0, l = e.changedTouches.length; i < l; ++i) {
                var touch = e.changedTouches[i]
                var slot = slotted[touch.identifier]
                var x = touch.pageX - screen.bounds.x
                var y = touch.pageY - screen.bounds.y
                var pressure = touch.force || 0.5
                var scaled = scaler.coords(
                    screen.bounds.w, screen.bounds.h, x, y, screen.rotation
                )

                touchMove(nextSeq(), slot, scaled.xP, scaled.yP, pressure)
                activateFinger(slot, x, y, pressure)
            }

            touchCommit(nextSeq())
        }

        function touchEndListener(event) {
            var e = event
            if (e.originalEvent) {
                e = e.originalEvent
            }

            var foundAny = false

            for (var i = 0, l = e.changedTouches.length; i < l; ++i) {
                var touch = e.changedTouches[i]
                var slot = slotted[touch.identifier]
                if (typeof slot === 'undefined') {
                    // We've already disposed of the contact. We may have gotten a
                    // touchend event for the same contact twice.
                    continue
                }
                delete slotted[touch.identifier]
                slots.push(slot)
                touchUp(nextSeq(), slot)
                deactivateFinger(slot)
                foundAny = true
            }

            if (foundAny) {
                touchCommit(nextSeq())
                if (!e.touches.length) {
                    stopTouching()
                }
            }
        }

        function startTouching() {
            gestureStart(nextSeq())
        }

        function stopTouching() {
            element.unbind('touchmove', touchMoveListener)
            $document.unbind('touchend', touchEndListener)
            $document.unbind('touchleave', touchEndListener)
            deactivateFingers()
            gestureStop(nextSeq())
        }

        element.on('touchstart', touchStartListener)
        element.on('mousedown', mouseDownListener)
        element.on('mouseup', mouseUpBugWorkaroundListener)
        $('#' + eleid).on('offsc', function() {
            panel.unbind()
            element.off()
        })


        panel.find('#home').on('click', home)
        panel.find('#menu').on('click', menu)
        panel.find('#back').on('click', back)
        panel.find('#power').on('click', power)
        panel.find('#volumeOff').on('click', volumeOff)
        panel.find('#volumeDown').on('click', volumeDown)
        panel.find('#volumeUp').on('click', volumeUp)
        createSlots()
    })()

    function sendOneWay(eventname, data) {
        // console.log(eventname, data, serial)
        if (map.length == 0 || (map.length == 1 && map[0] == serial)) {
            actionSocket.emit(eventname, { 'key': [serial], 'data': data })
        } else {
            if (map.indexOf(serial) < 0) {
                actionSocket.emit(eventname, { 'key': map.concat([serial]), 'data': data })
            } else {
                actionSocket.emit(eventname, { 'key': map, 'data': data })
            }
        }
    }



    function lock() {
        console.log('lock1')
        sendOneWay('setlockStatue', { 'enabled': true })
    }

    function unlock() {
        sendOneWay('setlockStatue', { 'enabled': false })
    }

    function touchDown(seq, contact, x, y, pressure) {
        sendOneWay('touchDown', { seq: seq, contact: contact, x: x, y: y, pressure: pressure })
    }

    function touchMove(seq, contact, x, y, pressure) {
        sendOneWay('touchMove', { seq: seq, contact: contact, x: x, y: y, pressure: pressure })
    }

    function touchUp(seq, contact) {
        sendOneWay('touchUp', { seq: seq, contact: contact })
    }

    function touchCommit(seq) {
        sendOneWay('touchCommit', { seq, seq })
    }

    function touchReset(seq) {
        sendOneWay('touchReset', { seq, seq })
    }

    function gestureStart(seq) {
        sendOneWay('gestureStart', { seq: seq })
    }

    function gestureStop(seq) {
        sendOneWay('gestureStop', { seq: seq })
    }
}
