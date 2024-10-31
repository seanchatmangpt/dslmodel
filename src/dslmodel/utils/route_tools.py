import re
from typing import List, Dict, Union

# Define types for segments
SegmentType = Union['static', 'dynamic', 'optional', 'catchall']


class ParsedPathSegmentToken:
    def __init__(self, type: SegmentType, value: str):
        self.type = type
        self.value = value


class ParsedPathSegment(List[ParsedPathSegmentToken]):
    pass


class ParsedPath(List[ParsedPathSegment]):
    pass


# Utility function to sanitize capture group names for regex
def sanitize_capture_group(name: str) -> str:
    return re.sub(r'(^\d|[^a-zA-Z0-9_])', '_', name)


# Function to parse individual segments
def parse_segment(segment: str) -> ParsedPathSegment:
    tokens = []
    i, buffer, state = 0, '', 'initial'

    while i < len(segment):
        char = segment[i]

        if state == 'initial':
            buffer = ''
            if char == '[':
                state = 'dynamic'
            else:
                state = 'static'
                buffer += char

        elif state == 'static':
            if char == '[':
                tokens.append(ParsedPathSegmentToken('static', buffer))
                buffer, state = '', 'dynamic'
            else:
                buffer += char

        elif state == 'dynamic':
            if char == ']':
                tokens.append(ParsedPathSegmentToken('dynamic', buffer))
                buffer, state = '', 'initial'
            else:
                buffer += char

        i += 1

    if buffer:
        tokens.append(ParsedPathSegmentToken(state, buffer))
    return ParsedPathSegment(tokens)


# Function to parse entire path into segments
def parse_path(path: str) -> ParsedPath:
    return [parse_segment(seg) for seg in path.strip('/').split('/')]


# toRegex: Converts path into a Python regular expression for matching
def to_regex(path: Union[str, ParsedPath]) -> re.Pattern:
    segments = parse_path(path) if isinstance(path, str) else path
    regex = '^'

    for segment in segments:
        for token in segment:
            if token.type == 'static':
                regex += re.escape(token.value)
            elif token.type == 'dynamic':
                regex += f"(?P<{sanitize_capture_group(token.value)}>[^/]+)"
            elif token.type == 'optional':
                regex += f"(?P<{sanitize_capture_group(token.value)}>[^/]*)"
            elif token.type == 'catchall':
                regex += f"(?P<{sanitize_capture_group(token.value)}>.*)"
        regex += "/?"

    regex += '$'
    return re.compile(regex)


# toSvelteKit: Converts path into a SvelteKit-compatible route format
def to_sveltekit(path: Union[str, ParsedPath]) -> str:
    segments = parse_path(path) if isinstance(path, str) else path
    svelte_path = '/'

    for segment in segments:
        svelte_segment = ''
        for token in segment:
            if token.type == 'static':
                svelte_segment += token.value
            elif token.type == 'dynamic':
                svelte_segment += f"[{token.value}]"
            elif token.type == 'optional':
                svelte_segment += f"[{token.value}]?"
            elif token.type == 'catchall':
                svelte_segment += f"[...{token.value}]"
        if svelte_segment:
            svelte_path += svelte_segment + '/'

    return svelte_path.rstrip('/')


# toSolidStart: Converts path into a SolidStart-compatible route format
def to_solidstart(path: Union[str, ParsedPath]) -> str:
    segments = parse_path(path) if isinstance(path, str) else path
    solid_path = '/'

    for segment in segments:
        solid_segment = ''
        for token in segment:
            if token.type == 'static':
                solid_segment += token.value
            elif token.type == 'dynamic':
                solid_segment += f":{token.value}"
            elif token.type == 'optional':
                solid_segment += f":{token.value}?"
            elif token.type == 'catchall':
                solid_segment += f"*{token.value}"
        if solid_segment:
            solid_path += solid_segment + '/'

    return solid_path.rstrip('/')


# toVueRouter: Converts path into a Vue Router-compatible route format
def to_vuerouter(path: Union[str, ParsedPath]) -> Dict[str, str]:
    segments = parse_path(path) if isinstance(path, str) else path
    vue_path = '/'

    for segment in segments:
        vue_segment = ''
        for token in segment:
            if token.type == 'static':
                vue_segment += token.value.replace(':', '\\:')
            elif token.type == 'dynamic':
                vue_segment += f":{token.value}()"
            elif token.type == 'optional':
                vue_segment += f":{token.value}?"
            elif token.type == 'catchall':
                vue_segment += f":{token.value}(.*)*"
        if vue_segment:
            vue_path += vue_segment + '/'

    return {'path': vue_path.rstrip('/')}


# toRadix: Converts path into a Radix-compatible route format
def to_radix(path: Union[str, ParsedPath]) -> str:
    segments = parse_path(path) if isinstance(path, str) else path
    radix_path = '/'

    for segment in segments:
        radix_segment = ''
        for token in segment:
            if token.type == 'static':
                radix_segment += token.value
            elif token.type == 'dynamic':
                radix_segment += f":{token.value}"
            elif token.type == 'optional':
                raise TypeError("Radix does not support optional parameters")
            elif token.type == 'catchall':
                radix_segment += f"**:{token.value}" if token.value else '**'

        if radix_segment:
            radix_path += radix_segment + '/'

    return radix_path.rstrip('/')


# Main function to test each route converter
if __name__ == "__main__":
    path = "/user/[id]/profile"

    # Parse the path into segments
    parsed_path = parse_path(path)
    print("Parsed Path:", parsed_path)

    # Generate regex route
    regex_route = to_regex(parsed_path)
    print("Regex Route:", regex_route)

    # Generate SvelteKit route
    sveltekit_route = to_sveltekit(parsed_path)
    print("SvelteKit Route:", sveltekit_route)

    # Generate SolidStart route
    solidstart_route = to_solidstart(parsed_path)
    print("SolidStart Route:", solidstart_route)

    # Generate Vue Router route
    vuerouter_route = to_vuerouter(parsed_path)
    print("Vue Router Route:", vuerouter_route)

    # Generate Radix route
    radix_route = to_radix(parsed_path)
    print("Radix Route:", radix_route)

    # Test matching a path with regex route
    test_path = "/user/123/profile"
    if regex_route.match(test_path):
        print(f"Path '{test_path}' matches!")
    else:
        print(f"Path '{test_path}' does not match.")
