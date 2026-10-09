from js import document, window
from pyodide.ffi import create_proxy


PAGE_DIRECTORY = str(window.location.pathname).rsplit("/", 1)[0]
RESOURCE_PREFIX = "../" if PAGE_DIRECTORY.endswith("/html") else ""
IMAGE_DIRECTORY = f"{RESOURCE_PREFIX}product_images/"
STORE_ASSET_DIRECTORY = f"{RESOURCE_PREFIX}store_assets/"


def show_preview(preview_button):
    card = preview_button.closest(".product-card")
    image = card.querySelector(".product-image")
    image.src = f"{IMAGE_DIRECTORY}{preview_button.getAttribute('data-image')}"
    image.alt = preview_button.getAttribute("data-name")
    for option in card.querySelectorAll(".preview-option"):
        option.setAttribute("aria-pressed", str(option == preview_button).lower())


def restore_original_image(event):
    card = event.target.closest(".product-card")
    if card is None:
        return

    next_target = event.relatedTarget
    if next_target is not None and card.contains(next_target):
        return

    image = card.querySelector(".product-image")
    image.src = f"{IMAGE_DIRECTORY}{image.getAttribute('data-original-image')}"
    image.alt = image.getAttribute("data-original-name")
    for option in card.querySelectorAll(".preview-option"):
        is_original = option.getAttribute("data-image") == image.getAttribute(
            "data-original-image"
        )
        option.setAttribute("aria-pressed", str(is_original).lower())


def ensure_preview_selector(card):
    preview_selector = card.querySelector(".product-preview-selector")
    if preview_selector is not None:
        return preview_selector

    shoe_cards = document.querySelectorAll("#shoe-grid .product-card")
    card_index = next(
        (index for index, shoe_card in enumerate(shoe_cards) if shoe_card == card),
        None,
    )
    if card_index is None or not shoe_cards:
        return None

    preview_selector = document.createElement("div")
    preview_selector.className = "product-preview-selector"
    preview_selector.setAttribute("aria-label", "Shoe image previews")

    current_card = shoe_cards[card_index]
    next_card = shoe_cards[(card_index + 1) % len(shoe_cards)]
    for preview_card in (current_card, next_card):
        preview_image = preview_card.querySelector(".product-image")
        image_name = preview_image.getAttribute("data-original-image")
        shoe_name = preview_image.getAttribute("data-original-name")
        if not image_name:
            continue

        option = document.createElement("button")
        option.type = "button"
        option.className = "preview-option"
        option.setAttribute("aria-pressed", str(preview_card == current_card).lower())
        option.setAttribute("aria-label", f"Preview {shoe_name} image")
        option.setAttribute("data-image", image_name)
        option.setAttribute("data-name", shoe_name)
        product_link = preview_card.querySelector(".product-image-link")
        if product_link is not None:
            option.setAttribute("data-product-url", product_link.getAttribute("href"))

        thumbnail = document.createElement("img")
        thumbnail.src = f"{IMAGE_DIRECTORY}{image_name}"
        thumbnail.alt = ""
        thumbnail.loading = "lazy"
        option.append(thumbnail)
        preview_selector.append(option)

    card.append(preview_selector)
    return preview_selector


def handle_catalog_click(event):
    preview_button = event.target.closest(".preview-option")
    if preview_button is not None:
        product_url = preview_button.getAttribute("data-product-url")
        if product_url:
            window.location.href = product_url
        return

    favorite_button = event.target.closest(".favorite-button")
    if favorite_button is not None:
        is_favorite = favorite_button.getAttribute("aria-pressed") != "true"
        favorite_button.setAttribute("aria-pressed", str(is_favorite).lower())
        favorite_button.setAttribute(
            "aria-label",
            "Remove from favorites" if is_favorite else "Add to favorites",
        )
        favorite_button.querySelector(".favorite-icon").src = (
            f"{STORE_ASSET_DIRECTORY}favorite_2.svg"
            if is_favorite
            else f"{STORE_ASSET_DIRECTORY}favorite.svg"
        )


def handle_detail_click(event):
    size_button = event.target.closest(".size-option")
    if size_button is not None:
        for option in document.querySelectorAll(".size-option"):
            option.setAttribute("aria-pressed", str(option == size_button).lower())
        document.querySelector("#product-action-status").textContent = ""
        return

    thumbnail = event.target.closest(".product-thumbnail")
    if thumbnail is not None:
        main_image = document.querySelector("#gallery-main-image")
        main_image.src = f"{IMAGE_DIRECTORY}{thumbnail.getAttribute('data-image')}"
        for option in document.querySelectorAll(".product-thumbnail"):
            option.setAttribute("aria-pressed", str(option == thumbnail).lower())
        return

    favorite_button = event.target.closest("#detail-favorite")
    if favorite_button is not None:
        is_favorite = favorite_button.getAttribute("aria-pressed") != "true"
        favorite_button.setAttribute("aria-pressed", str(is_favorite).lower())
        favorite_button.textContent = (
            "Favourite ♥" if is_favorite else "Favourite ♡"
        )
        return

    add_button = event.target.closest("#add-to-bag")
    if add_button is not None:
        selected_size = next(
            (
                option.getAttribute("data-size")
                for option in document.querySelectorAll(".size-option")
                if option.getAttribute("aria-pressed") == "true"
            ),
            None,
        )
        status = document.querySelector("#product-action-status")
        if selected_size is None:
            status.textContent = "Please select a size first."
            return
        status.textContent = f"Added to bag — {selected_size}."


def handle_preview_hover(event):
    preview_button = event.target.closest(".preview-option")
    if preview_button is not None:
        previous_target = event.relatedTarget
        if previous_target is not None and preview_button.contains(previous_target):
            return
        show_preview(preview_button)
        return

    card = event.target.closest(".product-card")
    if card is not None:
        ensure_preview_selector(card)


shoe_grid = document.querySelector("#shoe-grid")
if shoe_grid is not None:
    shoe_grid.addEventListener("click", create_proxy(handle_catalog_click))
    shoe_grid.addEventListener("mouseover", create_proxy(handle_preview_hover))
    shoe_grid.addEventListener("mouseout", create_proxy(restore_original_image))

if document.querySelector("#product-detail") is not None:
    document.addEventListener("click", create_proxy(handle_detail_click))
