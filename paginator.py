from urllib.parse import urlencode



class Paginator:
    
    def __init__(self, base_url, page, limit, total_records):
        print(base_url,'base irl')
        self.base_url = base_url
        self.page = page
        self.limit = limit
        self.total_records = total_records

        self.total_pages = (total_records + limit - 1) // limit
        self.has_next = self.page < self.total_pages
        self.has_previous = self.page > 1

    def get_next_url(self):
        if not self.has_next:
            return None
        return f"{self.base_url}?{urlencode({'page': self.page + 1, 'limit': self.limit})}"

    def get_previous_url(self):
        if not self.has_previous:
            return None
        return f"{self.base_url}?{urlencode({'page': self.page - 1, 'limit': self.limit})}"

    def get_pagination_meta(self):
        return {
            "page": self.page,
            "limit": self.limit,
            "total_records": self.total_records,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
            "next_url": self.get_next_url(),
            "previous_url": self.get_previous_url(),
            "data": []
        }
