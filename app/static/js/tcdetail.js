function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
}

var BLANK_IMG = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
var canvas = document.getElementById('canvas')
var g = canvas.getContext('2d')
    // screensocket=0
var serial = getQueryString("serial")
var screenSocket = io.connect("http://" + window.location.host + '/screen');
var actionSocket = io.connect("http://" + window.location.host + '/action');
var servicesSocket = io.connect("http://" + window.location.host + '/stfservice');
// alert(screenSocket.readyState)
screenSocket.binaryType = 'blob'

function close_screenScocket() {
    screenSocket.removeAllListeners()
    screenSocket.close()
    screenSocket = null
}

function close_actionSocket() {
    actionSocket.removeAllListeners()
    actionSocket.close()
    actionSocket = null
}

function close_servicesSocket() {
    servicesSocket.removeAllListeners()
    servicesSocket.close()
    servicesSocket = null
}
var imagePool = new ImagePool(10)
var screen = {
        rotation: 0,
        bounds: {
            x: 0,
            y: 0,
            w: 0,
            h: 0
        }
    }
    /**
     * Simple image pool
     */
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

/**
 * screenSocket listener
 */
screenSocket.on('connect', function() {
    console.log('connected')
})
screenSocket.on('testdata', function(data) {
    console.log(data)
})
screenSocket.on('disconnect', function() {
    console.log('disconnected')
})
screenSocket.on('imgdata' + getQueryString("serial"), function(data) {
    // console.log('data',data)
    var blob = new Blob([data], { type: 'image/jpeg' })
    var URL = window.URL || window.webkitURL
    var img = imagePool.next()
    img.onload = function() {
        canvas.width = img.width
        canvas.height = img.height
        g.drawImage(img, 0, 0)
        img.onload = img.onerror = null
        img.src = BLANK_IMG
        img = null
        blob = null

        URL.revokeObjectURL(url)
        url = null
    }
    var url = URL.createObjectURL(blob)
    img.src = url
})
screenSocket.on('errormsg' + getQueryString("serial"), function(data) {
    console.log(data)
    alert(data.msg)

    close_screenScocket()
})

$document = $(document)

// alert(getQueryString("uid")); 


function messageListener(message) {

}

element = $('#hahaha')
var input = element.find('input')

function send() {
    console.log('fuck')
    actionSocket.emit('point', { 'x': x, 'y': y });
}

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

var scaler = ScalingServiceFactory().coordinator(
    1152, 1920
)
var cssTransform = VendorUtilFactory().style(['transform', 'webkitTransform'])
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
    console.log(x, y)
    touchDown(nextSeq(), 0, scaled.xP, scaled.yP, pressure)
    console.log(scaled.xP, scaled.yP, 'process')

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
        touchUp(nextSeq(), 1, 1)
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

    touchUp(nextSeq(), 0, 2)

    if (fakePinch) {
        touchUp(nextSeq(), 1, 3)
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
    alert(e.originalEvent)
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
        touchUp(nextSeq(), slot, 4)
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

createSlots()
    //
function testdata() {
    $.getJSON($SCRIPT_ROOT + 'testdata', function(data) {});
}

function restart() {
    console.log('it is me')
    if (screenSocket != null) {
        close_screenScocket()
    }
    window.location = "http://" + window.location.host + '/testcase/jump'
}
//keyboard
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
        control.keyPress('switch_charset')
        return true
    }

    return false
}

function keydownListener(e) {
    // Prevent tab from switching focus to the next element, we only want
    // that to happen on the device side.
    if (e.keyCode === 9) {
        e.preventDefault()
    }
    keyDown(e.keyCode)
}

function keyupListener(e) {
    if (!handleSpecialKeys(e)) {
        keyUp(e.keyCode)
    }
}

function pasteListener(e) {
    // Prevent value change or the input event sees it. This way we get
    // the real value instead of any "\n" -> " " conversions we might see
    // in the input value.
    e.preventDefault()
    paste(e.clipboardData.getData('text/plain'))
}

// function copyListener(e) {
//   e.preventDefault()
//   // This is asynchronous and by the time it returns we will no longer
//   // have access to setData(). In other words it doesn't work. Currently
//   // what happens is that on the first copy, it will attempt to fetch
//   // the clipboard contents. Only on the second copy will it actually
//   // copy that to the clipboard.
//   control.getClipboardContent()
//   if (control.clipboardContent) {
//     e.clipboardData.setData('text/plain', control.clipboardContent)
//   }
// }

function inputListener() {
    // Why use the input event if we don't let it handle pasting? The
    // reason is that on latest Safari (Version 8.0 (10600.1.25)), if
    // you use the "Romaji" Kotoeri input method, we'll never get any
    // keypress events. It also causes us to lose the very first keypress
    // on the page. Currently I'm not sure if we can fix that one.
    typeaa(this.value)
    this.value = ''
}

input.bind('keydown', keydownListener)
input.bind('keyup', keyupListener)
input.bind('input', inputListener)
input.bind('paste', pasteListener)
    // input.bind('copy', copyListener)

//keyboard end
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
    console.log('iamin')
    return function(key) {
        console.log(typeof key === 'string')
        if (typeof key === 'string') {
            console.log('sendt')
            sendOneWay(type, {
                key: key
            })
        } else {
            var mapped = fixedKey || KeycodesMapped[key]
            if (mapped) {
                console.log('sent2' + type)
                sendOneWay(type, {
                    key: mapped
                })
            }
        }
    }
}


function typeaa(text) {
    console.log('type' + text)
    sendOneWay('type', {
        text: text
    })
}

function keyDown(key) {
    console.log('keydown' + key)
    temp = keySender('keyDown')
    temp(key)
}

function keyUp(key) {
    console.log('keyUp' + key)
    keySender('keyUp')(key)
}

function keyPress(key) {
    console.log('keyPress')
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

function sendOneWay(eventname, data) {
    actionSocket.emit(eventname, { 'key': serial, 'data': data })
}

function touchDown(seq, contact, x, y, pressure) {
    sendOneWay('touchDown', { seq: seq, contact: contact, x: x, y: y, pressure: pressure })
}

function touchMove(seq, contact, x, y, pressure) {
    console.log('move')
    sendOneWay('touchMove', { seq: seq, contact: contact, x: x, y: y, pressure: pressure })
}

function touchUp(seq, contact, f) {
    console.log('up', f)
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
