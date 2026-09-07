#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: ghcr_tags
short_description: Fetch every tag for a ghcr.io repo (including lscr.io mirrors) in one task
description:
  - Requests an anonymous GHCR pull token for the given repo, then fetches
    every page of its tag list, following the registry's Link response
    header, up to max_pages pages.
  - Does the whole thing inside a single Python process, in one Ansible
    task — no recursive include_tasks needed, which is both far faster
    and avoids the run_once-doesn't-dedupe-dynamic-includes problem that
    a recursive-include version runs into across multiple hosts.
  - Uses only the Python standard library (urllib) — nothing extra to
    install on the control node.
options:
  repo:
    description:
      - The image path with the registry host stripped, e.g.
        "linuxserver/sonarr" (not "lscr.io/linuxserver/sonarr").
    required: true
    type: str
  max_pages:
    description: Safety cap on how many pages to follow before giving up.
    required: false
    type: int
    default: 50
  page_size:
    description: Tags requested per page (registry may return fewer).
    required: false
    type: int
    default: 1000
author:
  - Written for the container_watchtower role
'''

EXAMPLES = r'''
- name: Fetch all tags for a GHCR repo
  ghcr_tags:
    repo: "linuxserver/sonarr"
    max_pages: 20
  register: sonarr_tags

- debug:
    msg: "{{ sonarr_tags.tags | length }} tags found across {{ sonarr_tags.page_count }} pages"
'''

RETURN = r'''
tags:
  description: Every tag name found, across all pages fetched.
  returned: success
  type: list
  elements: str
page_count:
  description: How many pages were actually fetched.
  returned: success
  type: int
truncated:
  description: >-
    True if max_pages was hit while a next-page link still existed
    (i.e. we gave up before the registry actually ran out of pages).
  returned: success
  type: bool
'''

import json
import re
import urllib.request
import urllib.error

from ansible.module_utils.basic import AnsibleModule


def fetch_json(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode('utf-8')
        link_header = resp.headers.get('Link', '') or ''
        return json.loads(body), link_header


def next_page_url(link_header):
    """
    Parses a standard OCI/Docker-Registry Link header, e.g.:
        <https://ghcr.io/v2/org/repo/tags/list?n=1000&last=X>; rel="next"
    Returns the absolute next-page URL, or None if there isn't one.
    """
    if not link_header or 'rel="next"' not in link_header:
        return None
    match = re.search(r'<([^>]+)>', link_header)
    if not match:
        return None
    url = match.group(1)
    if not url.startswith('http'):
        url = 'https://ghcr.io' + url
    return url


def run_module():
    module_args = dict(
        repo=dict(type='str', required=True),
        max_pages=dict(type='int', required=False, default=50),
        page_size=dict(type='int', required=False, default=1000),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    repo = module.params['repo']
    max_pages = module.params['max_pages']
    page_size = module.params['page_size']

    result = dict(changed=False, tags=[], page_count=0, truncated=False)

    try:
        token_url = "https://ghcr.io/token?scope=repository:%s:pull&service=ghcr.io" % repo
        token_data, _ = fetch_json(token_url)
        token = token_data.get('token')
        if not token:
            module.fail_json(msg="No token returned by ghcr.io for repo %s" % repo, **result)
            return

        headers = {'Authorization': 'Bearer %s' % token}
        url = "https://ghcr.io/v2/%s/tags/list?n=%d" % (repo, page_size)

        all_tags = []
        pages = 0

        while url and pages < max_pages:
            data, link_header = fetch_json(url, headers=headers)
            all_tags.extend(data.get('tags', []) or [])
            pages += 1
            url = next_page_url(link_header)

        result['tags'] = all_tags
        result['page_count'] = pages
        # A URL remaining here means we stopped because of max_pages,
        # not because the registry ran out of pages.
        result['truncated'] = bool(url)

        module.exit_json(**result)

    except urllib.error.HTTPError as e:
        module.fail_json(msg="HTTP error fetching tags for %s: %s" % (repo, e), **result)
    except Exception as e:
        module.fail_json(msg="Error fetching tags for %s: %s" % (repo, e), **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
