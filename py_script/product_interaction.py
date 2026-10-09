from js import document
from pyodide.ffi import create_proxy


SHOES = [
    {"image": "p1.png", "name": "Shoe 1", "price": "Price not set"},
    {"image": "p2.png", "name": "Shoe 2", "price": "Price not set"},
    {"image": "p3.png", "name": "Shoe 3", "price": "Price not set"},
    {"image": "p4.png", "name": "Shoe 4", "price": "Price not set"},
    {"image": "p5.png", "name": "Shoe 5", "price": "Price not set"},
    {"image": "p6.png", "name": "Shoe 6", "price": "Price not set"},
    {"image": "p7.png", "name": "Shoe 7", "price": "Price not set"},
    {"image": "p8.png", "name": "Shoe 8", "price": "Price not set"},
    {"image": "p9.png", "name": "Shoe 9", "price": "Price not set"},
    {"image": "p10.png", "name": "Shoe 10", "price": "Price not set"},
    {"image": "p11.png", "name": "Shoe 11", "price": "Price not set"},
]


shoe_grid = document.querySelector("#shoe-grid")
shoe_card_template = document.querySelector("#shoe-card-template")

for shoe in SHOES:
    card = shoe_card_template.content.cloneNode(True)
    image = card.querySelector(".product-image")
    image.src = f"../product_images/{shoe['image']}"
    image.alt = shoe["name"]
    card.querySelector(".product-name").textContent = shoe["name"]
    card.querySelector(".product-price").textContent = shoe["price"]
    shoe_grid.append(card)


def toggle_favorite(event):
    favorite_button = event.target.closest(".favorite-button")
    if favorite_button is None:
        return

    is_favorite = favorite_button.getAttribute("aria-pressed") == "true"
    is_favorite = not is_favorite
    favorite_button.setAttribute("aria-pressed", str(is_favorite).lower())
    favorite_button.setAttribute(
        "aria-label",
        "Remove from favorites" if is_favorite else "Add to favorites",
    )
    favorite_button.querySelector(".favorite-icon").src = (
        "../store_assets/favorite_2.svg"
        if is_favorite
        else "../store_assets/favorite.svg"
    )


favorite_click_handler = create_proxy(toggle_favorite)
shoe_grid.addEventListener("click", favorite_click_handler)
