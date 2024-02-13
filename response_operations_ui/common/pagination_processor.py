import math


def pagination_processor(total_results, page_limit, current_page_number, href=None):
    page_links = []
    total_results = math.ceil(total_results / page_limit)
    if href is None:
        href = "?page="
    else:
        href = href + "&page="
    for page_number in range(1, (total_results + 1)):
        page_link = {"url": href + str(page_number)}
        page_links.append(page_link)

    pagination = {
        "page_links": page_links,
        "current_page_number": current_page_number,
    }
    return pagination
