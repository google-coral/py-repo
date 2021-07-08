# Lint as: python3
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import collections
import hashlib
import json
import os
import re
import sys
import urllib.request


def normalize(name):
  return re.sub(r'[-_.]+', '-', name).lower()


def write(directory, filename, data):
  try:
    os.mkdir(directory)
  except FileExistsError:
    pass
  with open(os.path.join(directory, filename), 'w') as f:
    f.write(data)


def url_sha256(url):
  response = urllib.request.urlopen(url)
  return hashlib.sha256(response.read()).hexdigest()


def repo_index_html(all_wheels):
  content = '\n      '.join(
      f'<li><a href="{name}/">{name}</a></li>' for name in all_wheels.keys())
  return f"""<!DOCTYPE html>
<html>
  <head><title>Coral PEP-503 Repository</title></head>
  <body>
    <ul>
      {content}
    </ul>
  </body>
</html>
"""


def repo_wheels_html(all_wheels):
  links = []
  for _, wheels in all_wheels.items():
    for wheel_name, wheel_url in wheels:
      links.append(f'<a href="{wheel_url}">{wheel_name}</a><br/>')
  return '\n'.join(links)


def project_index_html(name, wheels):
  links = []
  for wheel_name, wheel_url in wheels:
    print('Processing: %s' % wheel_url)
    sha256 = url_sha256(wheel_url)
    print('  SHA256=%s' % sha256)
    links.append(f'<li><a href="{wheel_url}#sha256={sha256}">{wheel_name}</a></li>')

  content = '\n      '.join(links)
  return f"""<!DOCTYPE html>
<html>
  <head>
    <title>{name} wheels</title>
  </head>
  <body>
    <ul>
      {content}
    </ul>
  </body>
</html>
"""


def generate_repo(output_dir, all_wheels):
  write(output_dir, 'index.html',
        repo_index_html(all_wheels))

  write(output_dir, 'wheels.html',
        repo_wheels_html(all_wheels))

  for name, wheels in all_wheels.items():
    write(os.path.join(output_dir, name), 'index.html',
          project_index_html(name, wheels))


def get_all_wheels(github_owner, github_repo, keyword):
  # https://docs.github.com/en/rest/reference/repos#releases
  url = f'https://api.github.com/repos/{github_owner}/{github_repo}/releases'
  all_wheels = collections.defaultdict(list)

  with urllib.request.urlopen(url) as f:
    encoding = f.info().get_content_charset('utf-8')
    releases = json.loads(f.read().decode(encoding))
    for release in releases:
      for asset in release['assets']:
        name = asset['name']
        url = asset['browser_download_url']
        if name.endswith('.whl') and keyword in name:
          project = normalize(name.split('-')[0])
          all_wheels[project].append((name, url))

  for _, wheels in all_wheels.items():
    wheels.sort()

  return all_wheels


def main():
  parser = argparse.ArgumentParser(description='PEP 503 repo generator.')
  parser.add_argument('--output_dir', default='out',
                      help='output directory to save repo content')
  parser.add_argument('--keyword', default='',
                      help='keyword to filter .whl files')
  parser.add_argument('--github_owner', default='google-coral',
                      help='GitHub repo owner')
  parser.add_argument('--github_repo', default='pycoral',
                      help='GitHub repo name')
  args = parser.parse_args()

  output_dir = args.output_dir
  if os.path.exists(output_dir):
    print('Output directory "%s" already exists.' % output_dir, file=sys.stderr)
    return 1

  all_wheels = get_all_wheels(args.github_owner, args.github_repo, args.keyword)
  generate_repo(output_dir, all_wheels)
  return 0

if __name__ == '__main__':
  sys.exit(main())
