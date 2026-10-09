import json

from js import document
from pyodide.ffi import create_proxy


def get_selected_filters():
    selected_by_group = {}
    for checkbox in document.querySelectorAll(
        ".filter-sidebar input[data-filter-group]:checked"
    ):
        group = checkbox.getAttribute("data-filter-group")
        value = checkbox.getAttribute("data-filter-value")
        selected_by_group.setdefault(group, set()).add(value)
    return selected_by_group


def apply_filters_and_sort(_event=None):
    grid = document.querySelector("#shoe-grid")
    if grid is None:
        return

    cards = list(grid.querySelectorAll(".product-card"))
    selected_by_group = get_selected_filters()
    visible_count = 0

    for card in cards:
        tags = json.loads(card.getAttribute("data-tags") or "{}")
        matches = all(
            selected_values.intersection(tags.get(group, []))
            for group, selected_values in selected_by_group.items()
        )
        card.hidden = not matches
        visible_count += int(matches)

    sort_mode = document.querySelector("#shoe-sort").value
    if sort_mode == "name-asc":
        cards.sort(key=lambda card: card.getAttribute("data-name").casefold())
    elif sort_mode in ("price-asc", "price-desc"):
        priced_cards = [
            card for card in cards if card.getAttribute("data-price")
        ]
        unpriced_cards = [
            card for card in cards if not card.getAttribute("data-price")
        ]
        priced_cards.sort(
            key=lambda card: float(card.getAttribute("data-price")),
            reverse=sort_mode == "price-desc",
        )
        cards = priced_cards + unpriced_cards
    else:
        cards.sort(key=lambda card: int(card.getAttribute("data-catalog-index")))

    for card in cards:
        grid.append(card)

    status = document.querySelector("#filter-status")
    results = document.querySelector(".catalog-results")
    if results is not None:
        results.classList.toggle("is-empty", visible_count == 0)
    if status is not None:
        status.textContent = (
            f"Showing {visible_count} of {len(cards)} shoes"
            if visible_count
            else "No shoes match the selected filters."
        )


def on_catalog_ready(_event):
    apply_filters_and_sort()


filter_change_handler = create_proxy(apply_filters_and_sort)
sidebar = document.querySelector(".filter-sidebar")
if sidebar is not None:
    sidebar.addEventListener("change", filter_change_handler)

sort_select = document.querySelector("#shoe-sort")
if sort_select is not None:
    sort_select.addEventListener("change", filter_change_handler)

catalog_ready_handler = create_proxy(on_catalog_ready)
document.addEventListener("shoe-catalog-ready", catalog_ready_handler)
if document.querySelector("#shoe-grid .product-card") is not None:
    apply_filters_and_sort()
