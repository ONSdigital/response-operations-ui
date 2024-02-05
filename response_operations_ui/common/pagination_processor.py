import math


def pagination_processor(total_results, page_limit, page_number):
    page_links = []
    total_results = math.ceil(total_results / page_limit)
    for page_link in range(1, (total_results + 1)):
        page_links.append(page_link)

    pagination = {
        "page_links": page_links,
        "page": page_number,
    }
    return pagination
