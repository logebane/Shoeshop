def init_header_scroll_behavior():
    from js import document, window
    from pyodide.ffi import create_proxy

    header = document.querySelector("header")
    previous_scroll_y = window.scrollY

    def handle_scroll(_event):
        nonlocal previous_scroll_y

        current_scroll_y = window.scrollY
        scrolling_down = current_scroll_y > previous_scroll_y

        if current_scroll_y <= header.offsetHeight or not scrolling_down:
            header.classList.remove("header-hidden")
        else:
            header.classList.add("header-hidden")

        previous_scroll_y = current_scroll_y

    scroll_handler = create_proxy(handle_scroll)
    window.addEventListener("scroll", scroll_handler)


init_header_scroll_behavior()
