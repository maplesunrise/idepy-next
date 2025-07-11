window.idepy = {
  token: '%(token)s',
  platform: '%(platform)s',
  easy_resize: '%(easy_resize)s',
  api: {},
  _eventHandlers: {},
  _returnValues: {},

  _createApi: function (funcList) {
    function sanitize_params(params) {
      var reservedWords = (filtered_js_reserved_words = [
        'case',
        'catch',
        'const',
        'debugger',
        'default',
        'delete',
        'do',
        'export',
        'extends',
        'false',
        'function',
        'instanceof',
        'let',
        'new',
        'null',
        'super',
        'switch',
        'this',
        'throw',
        'true',
        'typeof',
        'var',
        'void',
      ]);

      for (var i = 0; i < params.length; i++) {
        var param = params[i];
        if (reservedWords.indexOf(param) !== -1) {
          params[i] = param + '_';
        }
      }

      return params;
    }

    for (var i = 0; i < funcList.length; i++) {
      var element = funcList[i];
      var funcName = element.func;
      var params = element.params;

      // Create nested structure and assign function
      var funcHierarchy = funcName.split('.');
      var functionName = funcHierarchy.pop();
      var nestedObject = funcHierarchy.reduce(function (obj, prop) {
        if (!obj[prop]) {
          obj[prop] = {};
        }
        return obj[prop];
      }, window.idepy.api);

      // Define the function body
      var funcBody =
        'var __id = (Math.random() + "").substring(2);' +
        'var promise = new Promise(function(resolve, reject) {' +
        '    window.idepy._checkValue("' +
        funcName +
        '", resolve, reject, __id);' +
        '});' +
        'window.idepy._jsApiCallback("' +
        funcName +
        '", Array.prototype.slice.call(arguments), __id);' +
        'return promise;';

      // Assign the new function
      nestedObject[functionName] = new Function(
        sanitize_params(params),
        funcBody
      );
      window.idepy._returnValues[funcName] = {};
    }
  },

  _jsApiCallback: function (funcName, params, id) {
    switch (window.idepy.platform) {
      case 'mshtml':
      case 'cef':
      case 'qtwebkit':
      case 'android-webkit':
        return window.external.call(funcName, idepy.stringify(params), id);
      case 'edgechromium':
        // Full file path support for WebView2
        if (
          params.event instanceof Event &&
          params.event.type === 'drop' &&
          params.event.dataTransfer.files
        ) {
          chrome.webview.postMessageWithAdditionalObjects(
            'FilesDropped',
            params.event.dataTransfer.files
          );
        }
        return window.chrome.webview.postMessage([
          funcName,
          idepy.stringify(params),
          id,
        ]);
      case 'cocoa':
      case 'gtkwebkit2':
        return window.webkit.messageHandlers.jsBridge.postMessage(
          idepy.stringify(
            { funcName: funcName, params: params, id: id }
          )
        );
      case 'qtwebengine':
        if (!window.idepy._QWebChannel) {
          setTimeout(function () {
            window.idepy._QWebChannel.objects.external.call(
              funcName,
              idepy.stringify(params),
              id
            );
          }, 100);
        } else {
          window.idepy._QWebChannel.objects.external.call(
            funcName,
            idepy.stringify(params),
            id
          );
        }
        break;
      default:
        break;
    }
  },

  _checkValue: function (funcName, resolve, reject, id) {
    var check = setInterval(function () {
      var returnObj = window.idepy._returnValues[funcName][id];
      if (returnObj) {
        var value = returnObj.value;
        var isError = returnObj.isError;

        delete window.idepy._returnValues[funcName][id];
        clearInterval(check);

        if (isError) {
          var pyError = JSON.parse(value);
          var error = new Error(pyError.message);
          error.name = pyError.name;
          error.stack = pyError.stack;

          reject(error);
        } else {
          resolve(JSON.parse(value));
        }
      }
    }, 1);
  },
  _asyncCallback: function (result, id) {
    window.idepy._jsApiCallback('idepyAsyncCallback', result, id);
  },
  _isPromise: function (obj) {
    return (
      !!obj &&
      (typeof obj === 'object' || typeof obj === 'function') &&
      typeof obj.then === 'function'
    );
  },

  stringify: function stringify(obj, timing) {
    function tryConvertToArray(obj) {
      try {
        return Array.prototype.slice.call(obj);
      } catch (e) {
        return obj;
      }
    }

    function isArrayLike(a) {
      return (
        a &&
        typeof a[Symbol.iterator] === 'function' &&
        typeof a.length === 'number' &&
        typeof a !== 'string'
      );
    }

    function serialize(obj, ancestors) {
      try {
        if (obj instanceof Node)
          return idepy.domJSON.toJSON(obj, {
            metadata: false,
            serialProperties: true,
          });
        if (obj instanceof Window) return 'Window';

        var boundSerialize = serialize.bind(obj);

        if (typeof obj !== 'object' || obj === null) {
          return obj;
        }

        while (
          ancestors.length > 0 &&
          ancestors[ancestors.length - 1] !== this
        ) {
          ancestors.pop();
        }

        if (ancestors.indexOf(obj) > -1) {
          return '[Circular Reference]';
        }
        ancestors.push(obj);

        if (isArrayLike(obj)) {
          obj = tryConvertToArray(obj);
        }

        if (Array.isArray(obj)) {
          var arr = obj.map(function (value) {
            return boundSerialize(value, ancestors);
          });
          return arr;
        }

        var newObj = {};
        for (var key in obj) {
          if (typeof obj === 'function') {
            continue;
          }
          newObj[key] = boundSerialize(obj[key], ancestors);
        }
        return newObj;
      } catch (e) {
        console.error(e);
        return e.toString();
      }
    }

    var startTime = +new Date();

    var _serialize = serialize.bind(null);
    var result = JSON.stringify(_serialize(obj, []));

    var endTime = +new Date();
    if (timing) {
      console.log('Serialization time: ' + (endTime - startTime) / 1000 + 's');
    }
    return result;
  },

  _getNodeId: function (element) {
    if (!element) {
      return null;
    }
    var idepyId =
      element.getAttribute('data-idepy-id') ||
      Math.random().toString(36).substr(2, 11);
    if (!element.hasAttribute('data-idepy-id')) {
      element.setAttribute('data-idepy-id', idepyId);
    }
    return idepyId;
  },

  _insertNode: function (node, parent, mode) {
    if (mode === 'LAST_CHILD') {
      parent.appendChild(node);
    } else if (mode === 'FIRST_CHILD') {
      parent.insertBefore(node, parent.firstChild);
    } else if (mode === 'BEFORE') {
      parent.parentNode.insertBefore(node, parent);
    } else if (mode === 'AFTER') {
      parent.parentNode.insertBefore(node, parent.nextSibling);
    } else if (mode === 'REPLACE') {
      parent.parentNode.replaceChild(node, parent);
    }
  },

  _loadCss: function (css) {
    var interval = setInterval(function () {
      if (document.readyState === 'complete') {
        clearInterval(interval);

        var cssElement = document.createElement('style');
        cssElement.type = 'text/css';
        cssElement.innerHTML = css;
        document.head.appendChild(cssElement);
      }
    }, 10);
  },

  _processElements: function (elements) {
    var serializedElements = [];

    for (var i = 0; i < elements.length; i++) {
      var idepyId;
      if (elements[i] === window) {
        idepyId = 'window';
      } else if (elements[i] === document) {
        idepyId = 'document';
      } else {
        idepyId = window.idepy._getNodeId(elements[i]);
      }

      var node = idepy.domJSON.toJSON(elements[i], {
        metadata: false,
        serialProperties: true,
        deep: false,
      });

      node._idepyId = idepyId;
      serializedElements.push(node);
    }

    return serializedElements;
  },

  _debounce: function (func, delay) {
    var timeout;
    return function () {
      var context = this;
      var args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(function () {
        func.apply(context, args);
      }, delay);
    };
  },
};

