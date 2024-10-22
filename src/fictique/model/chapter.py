class Chapter:
    def __init__(self, title: str, body: str, slot: int, fiction: int):
        self.title = title
        self.body = body
        self.slot = slot
        self.fiction = fiction

    def __repr__(self):
        return (f"Chapter(fiction={self.fiction!r}, slot={self.slot!r}, title={self.title!r}, "
                "body={len(self.body)} characters)")

    def __str__(self):
        return (f"Chapter[{self.fiction}/{self.slot}]: {self.title}\n"
                f"Body: {self.body[:100]}...")

    def full_text(self):
        return f"# {self.title}\n\n{self.body}"
