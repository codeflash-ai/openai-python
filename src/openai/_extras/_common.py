from .._exceptions import OpenAIError

INSTRUCTIONS = """

OpenAI error:

    missing `{library}`

This feature requires additional dependencies:

    $ pip install openai[{extra}]

"""


def format_instructions(*, library: str, extra: str) -> str:
    # Use f-string for more efficient string formatting
    return f"""

OpenAI error:

    missing `{library}`

This feature requires additional dependencies:

    $ pip install openai[{extra}]

"""


class MissingDependencyError(OpenAIError):
    pass
