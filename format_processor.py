class FormatProcessor:

    @classmethod
    def format_notification(cls, response):
        return f"> {response}"

    @classmethod
    def format_long_notification(cls, response):
        return f">>> {response}"

    @classmethod
    def format_table(cls, response):
        return f"```{response}```"
