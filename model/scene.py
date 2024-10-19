from .fiction import MD


class Scene:
    def __init__(self, title: str, summary: str, text: MD):
        self.title = title
        self.summary = summary
        self.text = text

    def __repr__(self):
        return f"Scene(title={self.title!r},summary={self.summary!r},text={len(self.text)} chars)"

    def __str__(self):
        return f"""## {self.title}
Word Count: {len(self.text.split())}
Paragraphs: {self.text.count("\n\n")}
Summary: {self.summary}
### Text (Excerpt):
{self.text[:100]} ... {self.text[-100:]}"""

    def to_markdown(self):
        return f"## {self.title}\n\nSummary: {self.summary}\n\n{self.text}"