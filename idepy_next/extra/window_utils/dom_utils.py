class GlobalEvent:
    click = "click"
    dblclick = "dblclick"
    mousedown = "mousedown"
    mouseup = "mouseup"
    mousemove = "mousemove"
    mouseenter = "mouseenter"
    mouseleave = "mouseleave"
    mouseover = "mouseover"
    mouseout = "mouseout"
    contextmenu = "contextmenu"
    wheel = "wheel"
    focus = "focus"
    blur = "blur"
    focusin = "focusin"
    focusout = "focusout"
    keydown = "keydown"
    keyup = "keyup"
    keypress = "keypress"
    input = "input"
    change = "change"
    submit = "submit"
    reset = "reset"
    scroll = "scroll"
    select = "select"
    error = "error"
    load = "load"
    unload = "unload"
    abort = "abort"
    beforeunload = "beforeunload"
    resize = "resize"


class ClipboardEvent:
    copy = "copy"
    cut = "cut"
    paste = "paste"


class CompositionEvent:
    compositionstart = "compositionstart"
    compositionupdate = "compositionupdate"
    compositionend = "compositionend"


class DragEvent:
    drag = "drag"
    dragstart = "dragstart"
    dragend = "dragend"
    dragenter = "dragenter"
    dragleave = "dragleave"
    dragover = "dragover"
    drop = "drop"


class MediaEvent:
    play = "play"
    pause = "pause"
    ended = "ended"
    timeupdate = "timeupdate"
    volumechange = "volumechange"
    durationchange = "durationchange"
    canplay = "canplay"
    canplaythrough = "canplaythrough"
    waiting = "waiting"
    loadeddata = "loadeddata"
    progress = "progress"
    loadstart = "loadstart"
    loadend = "loadend"
    stalled = "stalled"
    seeking = "seeking"
    seeked = "seeked"
    emptied = "emptied"
    suspend = "suspend"


class AnimationEvent:
    animationstart = "animationstart"
    animationiteration = "animationiteration"
    animationend = "animationend"


class TransitionEvent:
    transitionstart = "transitionstart"
    transitionend = "transitionend"
    transitionrun = "transitionrun"
    transitioncancel = "transitioncancel"


class PointerEvent:
    pointerdown = "pointerdown"
    pointerup = "pointerup"
    pointermove = "pointermove"
    pointercancel = "pointercancel"
    pointerover = "pointerover"
    pointerout = "pointerout"
    pointerenter = "pointerenter"
    pointerleave = "pointerleave"
    gotpointercapture = "gotpointercapture"
    lostpointercapture = "lostpointercapture"


class TouchEvent:
    touchstart = "touchstart"
    touchend = "touchend"
    touchmove = "touchmove"
    touchcancel = "touchcancel"


class InputEvent(GlobalEvent, ClipboardEvent, CompositionEvent): pass
class FormEvent(GlobalEvent): pass
class MediaElementEvent(GlobalEvent, MediaEvent): pass


class ElementEvent:
    # Global Events
    Div = GlobalEvent
    Span = GlobalEvent
    Canvas = GlobalEvent
    Label = GlobalEvent
    A = GlobalEvent
    Img = GlobalEvent
    Table = GlobalEvent
    Tr = GlobalEvent
    Td = GlobalEvent
    Li = GlobalEvent
    Ul = GlobalEvent
    Nav = GlobalEvent
    Section = GlobalEvent
    Header = GlobalEvent
    Footer = GlobalEvent
    Aside = GlobalEvent
    Main = GlobalEvent

    # Form elements
    Input = InputEvent
    Textarea = InputEvent
    Select = InputEvent
    Button = InputEvent
    Form = FormEvent

    # Media
    Audio = MediaElementEvent
    Video = MediaElementEvent

    # Specialized groups
    Clipboard = ClipboardEvent
    Composition = CompositionEvent
    Pointer = PointerEvent
    Animation = AnimationEvent
    Transition = TransitionEvent
    Touch = TouchEvent

    # Browser/document/window
    class Window(GlobalEvent):
        online = "online"
        offline = "offline"
        print_ = "print"
        beforeprint = "beforeprint"
        afterprint = "afterprint"
        hashchange = "hashchange"
        popstate = "popstate"
        storage = "storage"
        message = "message"


    class Document(GlobalEvent):
        DOMContentLoaded = "DOMContentLoaded"
        visibilitychange = "visibilitychange"
        readystatechange = "readystatechange"
        selectionchange = "selectionchange"

    class IdepyEvent:
        idepyready = "idepyready"


def bindElementEvent( element_query='document', event_type = None):
    """
    绑定元素事件，只作用WindowAPI生效的类。
    :param element_query: 绑定的元素查询器，输入document、window则使用相应对象，默认为document
    :param event_type:  绑定的元素事件，可以通过ElementEvent.Button.click获取相应类型的值。from idepy_next import bindElementEvent, ElementEvent
    :return:
    """
    def decorator(func):
        func._bind_event = (element_query, event_type)
        return func
    return decorator

def bindVueElementEvent( element_query='document', event_type = None):
    """
    绑定Vue元素事件，只作用WindowAPI生效的类。
    :param element_query: 绑定的元素查询器，输入document、window则使用相应对象，默认为document
    :param event_type:  绑定的元素事件，可以通过ElementEvent.Button.click获取相应类型的值。from idepy_next import bindElementEvent, ElementEvent
    :return:
    """
    def decorator(func):
        func._vue_bind_event = (element_query, event_type)
        return func
    return decorator



from typing import Optional, List

from idepy_next.dom.element import Element

class Elements:

    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    @property
    def window(self):
        return self._window.dom.window

    @property
    def document(self):
        return self._window.dom.document

    def element(self, selector) -> Optional[Element]:
        return self._window.dom.get_element(selector)

    def elements(self, selector) -> List[Element]:
        return self._window.dom.get_elements(selector)

