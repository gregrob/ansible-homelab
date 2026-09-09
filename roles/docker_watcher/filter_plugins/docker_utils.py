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


def split_image_ref(image):
    """
    Splits a Docker image reference into {'repo': ..., 'tag': ...},
    correctly handling two cases a naive split(':')[0] gets wrong:
      - a registry port, e.g. "myregistry.local:5000/app:1.0"
        -> repo="myregistry.local:5000/app", tag="1.0"
      - a digest pin, e.g. "nginx@sha256:abcd..."
        -> repo="nginx", tag="digest-pinned" (a digest isn't a movable
        tag, so it's surfaced as a clear sentinel rather than a fake
        version string that would never match any tag rule anyway)

    A plain "repo:tag" or bare "repo" (-> tag "latest") both still
    work exactly as before.
    """
    if '@' in image:
        return {'repo': image.split('@', 1)[0], 'tag': 'digest-pinned'}

    last_segment = image.rsplit('/', 1)[-1]
    if ':' in last_segment:
        repo, tag = image.rsplit(':', 1)
        return {'repo': repo, 'tag': tag}

    return {'repo': image, 'tag': 'latest'}


def pick_tag_regex(repo, tag_rules, default_regex):
    """
    Returns the regex from the first entry in tag_rules whose prefix
    matches repo — order decides priority, first match wins. Falls
    back to default_regex if nothing matches.

    A prefix ending in "/" matches as a family (e.g. "linuxserver/"
    matches any "linuxserver/<anything>"). A prefix NOT ending in "/"
    must match repo exactly (or be followed by "/") — this stops a
    single-token prefix like "postgres" from also matching an
    unrelated "postgres-exporter".
    """
    if not tag_rules:
        return default_regex

    for rule in tag_rules:
        prefix = rule.get('prefix', '')
        regex = rule.get('regex')
        if not (prefix and regex):
            continue
        if prefix.endswith('/'):
            if repo.startswith(prefix):
                return regex
        elif repo == prefix or repo.startswith(prefix + '/'):
            return regex

    return default_regex


class FilterModule(object):
    def filters(self):
        return {
            'get_latest_docker_tag': get_latest_docker_tag,
            'pick_tag_regex': pick_tag_regex,
            'split_image_ref': split_image_ref,
        }
