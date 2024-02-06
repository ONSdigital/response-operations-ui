import math


def pagination_processor(total_results, page_limit, current_page_number):
    page_numbers = []
    total_results = math.ceil(total_results / page_limit)
    for page_link in range(1, (total_results + 1)):
        page_numbers.append(page_link)

    pagination = {
        "page_numbers": page_numbers,
        "current_page_number": current_page_number,
    }
    return pagination
