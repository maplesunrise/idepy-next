(function() {
    var platform = window.idepy.platform;
    var disableText = '%(text_select)s' === 'False';
    var disableTextCss = 'body {-webkit-user-select: none; -khtml-user-select: none; -ms-user-select: none; user-select: none; cursor: default;}'

    if (platform == 'mshtml') {
        window.alert = function(msg) {
            window.external.alert(msg);
        }
    } else if (platform == 'edgechromium') {
        window.alert = function (message) {
            window.chrome.webview.postMessage(['_idepyAlert', idepy.stringify(message), 'alert']);
        }
    } else if (platform == 'gtkwebkit2') {
        window.alert = function (message) {
            window.webkit.messageHandlers.jsBridge.postMessage(idepy.stringify({funcName: '_idepyAlert', params: message, id: 'alert'}));
        }
    } else if (platform == 'cocoa') {
        window.print = function() {
            window.webkit.messageHandlers.browserDelegate.postMessage('print');
        }
    } else if (platform === 'qtwebengine') {
        window.alert = function (message) {
            window.idepy._QWebChannel.objects.external.call('_idepyAlert', idepy.stringify(message), 'alert');
        }
    } else if (platform === 'qtwebkit') {
        window.alert = function (message) {
            window.external.invoke(JSON.stringify(['_idepyAlert', message, 'alert']));
        }
    }

    if (disableText) {
        var css = document.createElement("style");
        css.type = "text/css";
        css.innerHTML = disableTextCss;
        document.head.appendChild(css);
    }

    function disableTouchEvents() {
        var initialX = 0;
        var initialY = 0;

        function onMouseMove(ev) {
            var x = ev.screenX - initialX;
            var y = ev.screenY - initialY;
            window.idepy._jsApiCallback('idepyMoveWindow', [x, y], 'move');
        }

        function onMouseUp() {
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        }

        function onMouseDown(ev) {
            initialX = ev.clientX;
            initialY = ev.clientY;
            window.addEventListener('mouseup', onMouseUp);
            window.addEventListener('mousemove', onMouseMove);
        }

        var dragBlocks = document.querySelectorAll('%(drag_selector)s');
        for (var i=0; i < dragBlocks.length; i++) {
            dragBlocks[i].addEventListener('mousedown', onMouseDown);
        }
            // easy drag for edge chromium
        if ('%(easy_drag)s' === 'True') {
            window.addEventListener('mousedown', onMouseDown);
        }

        if ('%(zoomable)s' === 'False') {
            document.body.addEventListener('touchstart', function(e) {
                if ((e.touches.length > 1) || e.targetTouches.length > 1) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                }
            }, {passive: false});

            window.addEventListener('wheel', function (e) {
                if (e.ctrlKey) {
                    e.preventDefault();
                }
            }, {passive: false});
        }

        // draggable
        if ('%(draggable)s' === 'False') {
            Array.prototype.slice.call(document.querySelectorAll("img")).forEach(function(img) {
                img.setAttribute("draggable", false);
            })

            Array.prototype.slice.call(document.querySelectorAll("a")).forEach(function(a) {
                a.setAttribute("draggable", false);
            })
        }
    }

    disableTouchEvents();

    // use easy resize
    if (window.idepy.easy_resize !== 'False') {
        function mountResizeHandles() {
  const interval = setInterval(() => {
  if (document.body) {
      appendResizeHandles();
      clearInterval(interval);
    }
  }, 50);

  function appendResizeHandles() {
const directions = [
  'top', 'bottom', 'left', 'right',
  'top-left', 'top-right', 'bottom-left', 'bottom-right'
];

const size = 8;

directions.forEach(dir => {
  const el = document.createElement('div');
  el.className = 'resize-handle ' + dir;
  el.style.position = 'absolute';
  el.style.zIndex = '9999';
  el.style.background = 'transparent';
  el.style.cursor = getCursor(dir);


  switch (dir) {
    case 'top': el.style.top = '0'; el.style.left = size + 'px'; el.style.right = size + 'px'; el.style.height = size + 'px'; break;
    case 'bottom': el.style.bottom = '0'; el.style.left = size + 'px'; el.style.right = size + 'px'; el.style.height = size + 'px'; break;
    case 'left': el.style.left = '0'; el.style.top = size + 'px'; el.style.bottom = size + 'px'; el.style.width = size + 'px'; break;
    case 'right': el.style.right = '0'; el.style.top = size + 'px'; el.style.bottom = size + 'px'; el.style.width = size + 'px'; break;
    case 'top-left': el.style.top = '0'; el.style.left = '0'; el.style.width = size + 'px'; el.style.height = size + 'px'; break;
    case 'top-right': el.style.top = '0'; el.style.right = '0'; el.style.width = size + 'px'; el.style.height = size + 'px'; break;
    case 'bottom-left': el.style.bottom = '0'; el.style.left = '0'; el.style.width = size + 'px'; el.style.height = size + 'px'; break;
    case 'bottom-right': el.style.bottom = '0'; el.style.right = '0'; el.style.width = size + 'px'; el.style.height = size + 'px'; break;
  }

  el.addEventListener('mousedown', () => {
      if(!window.idepy._jsApiCallback){
          return
      }
    window.idepy._jsApiCallback('idepyResizeStart', [dir], 'resize');
  });

  document.body.appendChild(el);
});

window.addEventListener('mouseup', () => {
   if(!window.idepy._jsApiCallback){
      return
  }
  window.idepy._jsApiCallback('idepyResizeStop', [], 'resize');
});

window.addEventListener('mousemove', () => {
    if(!window.idepy._jsApiCallback){
      return
    }
  window.idepy._jsApiCallback('idepyResizeMove', [], 'resize');
});
}

  function getCursor(dir) {
    switch (dir) {
      case 'top':
      case 'bottom': return 'ns-resize';
      case 'left':
      case 'right': return 'ew-resize';
      case 'top-left':
      case 'bottom-right': return 'nwse-resize';
      case 'top-right':
      case 'bottom-left': return 'nesw-resize';
    }
    return 'default';
  }
}
        mountResizeHandles()
    }



  })();

