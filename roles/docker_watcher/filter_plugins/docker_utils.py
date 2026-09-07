import re


def _extract_tag_names(results_list):
    """
    Normalises two different upstream shapes into a flat list of tag
    name strings:
      - Docker Hub: list of dicts, e.g. [{"name": "1.2.3", ...}, ...]
      - GHCR:       flat list of strings, e.g. ["1.2.3", "latest", ...]
    """
    names = []
    for item in results_list:
        if isinstance(item, dict):
            if 'name' in item:
                names.append(item['name'])
        elif isinstance(item, str):
            names.append(item)
    return names


def get_latest_docker_tag(results_list, regex_pattern):
    """
    Takes a list of tags (either Docker Hub's list-of-dicts or GHCR's
    flat list-of-strings — see _extract_tag_names), filters them by a
    regex, and sorts them safely by extracting purely numeric tuples.
    """
    if not results_list:
        return ""

    tag_names = _extract_tag_names(results_list)

    # 1. Extract only the tag names that match the strict regex
    valid_tags = [name for name in tag_names if re.match(regex_pattern, name)]

    if not valid_tags:
        return ""

    # 2. Define a bulletproof sorting mechanism
    # This turns 'v1.2.3-ls40' into (1, 2, 3, 40)
    # Python flawlessly sorts tuples of integers without crashing
    def extract_numeric_tuple(tag_string):
        numbers = re.findall(r'\d+', tag_string)
        return tuple(int(n) for n in numbers)

    # 3. Sort the tags using the numeric tuples and return the highest
    valid_tags.sort(key=extract_numeric_tuple)
    return valid_tags[-1]


def pick_tag_regex(repo, tag_rules, default_regex):
    """
    Walks an ORDERED list of {prefix, regex} dicts and returns the regex
    for the first entry whose prefix the repo starts with. Order is the
    only thing that decides priority — put more specific prefixes
    (e.g. 'linuxserver/sonarr') before more general ones
    (e.g. 'linuxserver/') in watchtower_tag_rules, since the first
    match wins and later entries are never consulted once one hits.

    Falls back to default_regex if nothing in the list matches.
    """
    if not tag_rules:
        return default_regex

    for rule in tag_rules:
        prefix = rule.get('prefix', '')
        regex = rule.get('regex')
        if prefix and regex and repo.startswith(prefix):
            return regex

    return default_regex


class FilterModule(object):
    def filters(self):
        return {
            'get_latest_docker_tag': get_latest_docker_tag,
            'pick_tag_regex': pick_tag_regex,
        }
