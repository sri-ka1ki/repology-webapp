# Copyright (C) 2016-2018 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

from repology.package import Package, PackageFlags
from repology.util import GetMaintainers


def SanitizeVersion(version):
    origversion = version

    version = re.sub('-r[0-9]+$', '', version)

    if version != origversion:
        return version, origversion
    else:
        return version, None


class ExherboGitParser():
    def __init__(self):
        pass

    def Parse(self, path):
        result = []

        maintainers = []

        with open(os.path.join(path, 'metadata/about.conf')) as metadata:
            for line in metadata:
                if '=' in line:
                    key, value = map(lambda s: s.strip(), line.split('=', 1))

                    if key == 'owner':
                        maintainers = GetMaintainers(value)

        packages_path = os.path.join(path, 'packages')

        for category in os.listdir(packages_path):
            category_path = os.path.join(packages_path, category)
            if not os.path.isdir(category_path):
                continue

            for package in os.listdir(category_path):
                package_path = os.path.join(category_path, package)
                if not os.path.isdir(package_path):
                    continue

                for exheres in os.listdir(package_path):
                    if not exheres.startswith(package + '-') and not exheres.endswith('.exheres-0'):
                        continue

                    pkg = Package()

                    pkg.category = category
                    pkg.name = package
                    pkg.version, pkg.origversion = SanitizeVersion(exheres[len(package) + 1:-10])
                    pkg.maintainers = maintainers

                    if pkg.version == 'scm' or pkg.version.endswith('-scm'):
                        pkg.SetFlag(PackageFlags.rolling)

                    result.append(pkg)

        return result
