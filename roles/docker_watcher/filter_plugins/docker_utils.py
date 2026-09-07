import re

def get_latest_docker_tag(results_list, regex_pattern):
    """
    Takes a list of Docker Hub tag dictionaries, filters them by a regex,
    and sorts them safely by extracting purely numeric tuples.
    """
    if not results_list:
        return ""

    # 1. Extract only the tag names that match the strict regex
    valid_tags = [
        tag['name'] for tag in results_list 
        if 'name' in tag and re.match(regex_pattern, tag['name'])
    ]

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

class FilterModule(object):
    def filters(self):
        return {
            'get_latest_docker_tag': get_latest_docker_tag
        }
