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
import hashlib
import os
import sys
import urllib.parse
import urllib.request


def get_sha256(url):
  response = urllib.request.urlopen(url)
  return hashlib.sha256(response.read()).hexdigest()


def package_wheels(package, base_url):
  name, version = package
  for py_version in ['cp35-cp35m', 'cp36-cp36m', 'cp37-cp37m', 'cp38-cp38']:
    for os_arch in ['linux_aarch64', 'linux_armv7l', 'linux_x86_64',
                    'win_amd64', 'macosx_10_15_x86_64']:
      escaped_name = name.replace('-', '_')
      wheel_name = f'{escaped_name}-{version}-{py_version}-{os_arch}.whl'
      yield wheel_name, f'{base_url}/{urllib.parse.quote(wheel_name)}'


def index_html(packages):
  content = '\n      '.join(
      f'<li><a href="{name}">{name}</a></li>' for name, version in packages)
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


def package_index_html(package, base_url):
  name, version = package

  links = []
  for wheel_name, wheel_url in package_wheels(package, base_url):
    print('Processing: %s' % wheel_url)
    sha256 = get_sha256(wheel_url)
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


def wheels_html(packages, base_url):
  links = []
  for package in packages:
    for wheel_name, wheel_url in package_wheels(package, base_url):
      links.append(f'<a href="{wheel_url}">{wheel_name}</a><br/>')
  return '\n'.join(links)


def generate(output_dir, packages, base_url):
  os.mkdir(output_dir)
  with open(os.path.join(output_dir, 'index.html'), 'w') as f:
    f.write(index_html(packages))

  for package in packages:
    package_dir = os.path.join(output_dir, package[0])
    os.mkdir(package_dir)
    with open(os.path.join(package_dir, 'index.html'), 'w') as f:
      f.write(package_index_html(package, base_url))

  with open(os.path.join(output_dir, 'wheels.html'), 'w') as f:
    f.write(wheels_html(packages, base_url))


def main():
  parser = argparse.ArgumentParser(description='PEP 503 repo generator.')
  parser.add_argument('--base_url', required=True,
                      help='base URL to download wheels')
  parser.add_argument('--output_dir', default='out',
                      help='output directory to save repo content')
  parser.add_argument('packages', metavar='N', type=str, nargs='+',
                      help='list of <package_name>@<package_version> strings')
  args = parser.parse_args()

  base_url = args.base_url
  packages = [tuple(package.split('@')) for package in args.packages]
  output_dir = args.output_dir

  if os.path.exists(output_dir):
    print('Output directory "%s" already exists.' % output_dir, file=sys.stderr)
    return 1

  generate(output_dir, packages, base_url)
  return 0

if __name__ == '__main__':
  sys.exit(main())
