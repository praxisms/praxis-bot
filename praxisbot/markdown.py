def preformat(title: str, content: str):
    """
    Produce a block of preformatted text with a title.

    :param title: the title, rendered as "normal" text
    :param content: the content, which will be wrapped in a pre block
    :return: the markdown
    """
    pre = "\n".join(["```", content, "```"])
    return f"{title}\n{pre}"
