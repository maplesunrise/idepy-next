window.idepy._createApi(JSON.parse('%(functions)s'));
if(window?.idepy?.api?.iglobal_auto_bind_events){
    window.idepy.api.iglobal_auto_bind_events()
}

if (window.idepy.platform == 'qtwebengine') {
  new QWebChannel(qt.webChannelTransport, function(channel) {
      window.idepy._QWebChannel = channel;
      window.dispatchEvent(new CustomEvent('idepyready'));
      window.dispatchEvent(new CustomEvent('pywebviewready'));
  });
} else {
  window.dispatchEvent(new CustomEvent('idepyready'));
  // poly fix pywebview
  window.pywebview = window.idepy
  window.dispatchEvent(new CustomEvent('pywebviewready'));
}
