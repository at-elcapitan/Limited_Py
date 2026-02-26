# AT PROJECT Limited 2022 - 2024; nEXT-v4.0_beta.1
class ParseException(Exception):
    def __init__(self, text):
        super().__init__(text)


def parse_input(string: str) -> set[int]:
    if not string.strip():
        raise ParseException("Input string is empty.")

    result: set[int] = set()
    tokens = [token.strip() for token in string.split(",") if token.strip()]

    for token in tokens:
        if "-" in token:
            parts = token.split("-")

            if len(parts) != 2:
                raise ParseException(f"Invalid range format `{token}`")

            try:
                start = int(parts[0]) - 1
                end = int(parts[1]) - 1
            except ValueError:
                raise ParseException(f"Unable to parse token `{token}`")

            if start > end:
                raise ParseException(
                    f"Invalid range `{token}`. Start cannot be greater than end."
                )

            result.update(range(start, end + 1))
            continue
        
        try:
            result.add(int(token) - 1)
        except ValueError:
            raise ParseException(f"Unable to parse token `{token}`")

    return result
