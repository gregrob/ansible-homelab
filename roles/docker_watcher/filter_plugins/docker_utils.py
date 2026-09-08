import re


def _extract_tag_names(results_list):
    """
    Normalises tag data from either registry shape into a flat list
    of tag name strings:
      - Docker Hub: list of dicts, e.g. [{"name": "1.2.3"}, ...]
      - GHCR:       flat list of strings, e.g. ["1.2.3", "latest"]
    """
    names = []
    for item in results_list:
        if isinstance(item, dict):
            if 'name' in item:
                names.append(item['name'])
        elif isinstance(item, str):
            names.append(item)
    return names


def _numeric_tuple(tag_string):
    """'v1.2.3-ls40' -> (1, 2, 3, 40), for safe numeric comparison."""
    return tuple(int(n) for n in re.findall(r'\d+', tag_string))


def get_latest_docker_tag(results_list, regex_pattern):
    """
    Filters tags to those matching regex_pattern, then returns the
    highest one by numeric tuple comparison. Returns "" if nothing
    matches.
    """
    if not results_list:
        return ""

    tag_names = _extract_tag_names(results_list)
    valid_tags = [name for name in tag_names if re.match(regex_pattern, name)]

    if not valid_tags:
        return ""

    valid_tags.sort(key=_numeric_tuple)
    return valid_tags[-1]


def pick_tag_regex(repo, tag_rules, default_regex):
    """
    Returns the regex from the first entry in tag_rules whose prefix
    matches repo — order decides priority, first match wins. Falls
    back to default_regex if nothing matches.
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
