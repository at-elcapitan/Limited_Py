# AT PROJECT Limited 2022 - 2024; AT_nEXT-v3.5.1
class ParseException(Exception):
    def __init__(self, text):
        super().__init__(text)


def parse_input(string: str) -> set:
    parsed_string = string.split(',')
    result = set()

    if (len(parsed_string) == 0):
        raise ParseException("Unable to parse string")

    for token in parsed_string:
        if "-" in token:
            parsed_token = token.split("-")
            try:
                parsed_token = [int(x) for x in parsed_token]
            except ValueError:
                raise ParseException(f"Unable to parse token `{token}`")

            if parsed_token[0] > parsed_token[1]:
                raise ParseException(f"Unable to parse token `{token}`."
                                     " First value is bigger than the second.")

            result.update(range(parsed_token[0] - 1, parsed_token[1]))
            continue

        try:
            result.add(int(token))
        except ValueError:
            raise ParseException(f"Unable to parse token `{token}`")

    return result
