import asyncio
import json
from urllib.parse import parse_qs

from js import document, window
from pyodide.http import pyfetch


IMAGE_DIRECTORY = "../product_images/"


async def load_shoes():
    response = await pyfetch("../data/shoes.json")
    if not response.ok:
        raise RuntimeError(f"Could not load shoe data (HTTP {response.status}).")
    return json.loads(await response.string())


def set_text(selector, value):
    element = document.querySelector(selector)
    if element is not None:
        element.textContent = value


def render_catalog(shoes):
    shoe_grid = document.querySelector("#shoe-grid")
    template = document.querySelector("#shoe-card-template")

    for shoe in shoes:
        card = template.content.cloneNode(True)
        card_element = card.querySelector(".product-card")
        card_element.setAttribute("data-name", shoe["name"])
        card_element.setAttribute("data-price", "" if shoe["price"] is None else str(shoe["price"]))
        card_element.setAttribute("data-tags", json.dumps(shoe.get("tags", {})))
        card_element.setAttribute("data-catalog-index", str(len(shoe_grid.children)))
        image = card.querySelector(".product-image")
        image.src = IMAGE_DIRECTORY + shoe["images"][0]
        image.alt = shoe["name"]
        image.setAttribute("data-original-image", shoe["images"][0])
        image.setAttribute("data-original-name", shoe["name"])

        product_link = card.querySelector(".product-image-link")
        product_link.href = f"product_preview.html?id={shoe['id']}"
        product_link.setAttribute("aria-label", f"View details for {shoe['name']}")
        name_link = card.querySelector(".product-name-link")
        name_link.href = f"product_preview.html?id={shoe['id']}"

        name_link.textContent = shoe["name"]
        card.querySelector(".product-price").textContent = (
            f"₱{shoe['price']:,.2f}" if shoe["price"] is not None else "Price not set"
        )
        card.querySelector(".product-category").textContent = shoe["category"]

        preview_selector = card.querySelector(".product-preview-selector")
        for preview_index, image_name in enumerate(shoe["images"]):
            preview_button = document.createElement("button")
            preview_button.type = "button"
            preview_button.className = "preview-option"
            preview_button.setAttribute(
                "aria-pressed", str(preview_index == 0).lower()
            )
            preview_button.setAttribute(
                "aria-label", f"Preview {shoe['name']} image {preview_index + 1}"
            )
            preview_button.setAttribute("data-image", image_name)
            preview_button.setAttribute("data-name", shoe["name"])

            preview_thumbnail = document.createElement("img")
            preview_thumbnail.src = IMAGE_DIRECTORY + image_name
            preview_thumbnail.alt = ""
            preview_thumbnail.loading = "lazy"
            preview_button.append(preview_thumbnail)
            preview_selector.append(preview_button)

        if len(shoe["images"]) < 2:
            preview_selector.remove()

        shoe_grid.append(card)

    document.dispatchEvent(window.Event.new("shoe-catalog-ready"))


def render_product(shoes):
    shoe_id = parse_qs(str(window.location.search).lstrip("?")).get("id", [None])[0]
    shoe = next((item for item in shoes if item["id"] == shoe_id), None)
    if shoe is None:
        document.querySelector("#product-not-found").hidden = False
        return

    document.querySelector("#product-detail").hidden = False
    set_text("#detail-name", shoe["name"])
    set_text("#detail-category", shoe["category"])
    set_text(
        "#detail-price",
        f"₱{shoe['price']:,.2f}" if shoe["price"] is not None else "Price not set",
    )
    main_image = document.querySelector("#gallery-main-image")
    main_image.src = IMAGE_DIRECTORY + shoe["images"][0]
    main_image.alt = shoe["name"]

    thumbnails = document.querySelector("#product-thumbnails")
    for image_index, image_name in enumerate(shoe["images"]):
        thumbnail = document.createElement("button")
        thumbnail.type = "button"
        thumbnail.className = "product-thumbnail"
        thumbnail.setAttribute("data-image", image_name)
        thumbnail.setAttribute("aria-label", f"Show {shoe['name']} image {image_index + 1}")
        thumbnail.setAttribute("aria-pressed", str(image_index == 0).lower())
        thumbnail_image = document.createElement("img")
        thumbnail_image.src = IMAGE_DIRECTORY + image_name
        thumbnail_image.alt = ""
        thumbnail.append(thumbnail_image)
        thumbnails.append(thumbnail)

    sizes = document.querySelector("#size-options")
    for size in shoe["sizes"]:
        size_button = document.createElement("button")
        size_button.type = "button"
        size_button.className = "size-option"
        size_button.textContent = size
        size_button.setAttribute("data-size", size)
        size_button.setAttribute("aria-pressed", "false")
        sizes.append(size_button)


async def initialize():
    try:
        shoes = await load_shoes()
    except Exception as error:
        status = document.querySelector("#data-status")
        if status is not None:
            status.textContent = f"Unable to load shoe information: {error}"
        raise

    if document.querySelector("#shoe-grid") is not None:
        render_catalog(shoes)
        status = document.querySelector("#data-status")
        if status is not None:
            status.hidden = True
    elif document.querySelector("#product-detail") is not None:
        status = document.querySelector("#data-status")
        if status is not None:
            status.hidden = True
        document.querySelector("#product-detail").hidden = True
        render_product(shoes)

asyncio.ensure_future(initialize())
