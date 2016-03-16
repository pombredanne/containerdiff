#   Container Diff tool - show differences among container images
#
#   Copyright (C) 2015 Marek Skalický mskalick@redhat.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#

""" Show diff in container image history.
"""

import undocker
import difflib
import docker

def dockerfile_from_image(ID, cli):
    """ Return list of commands used to create image *ID*. Thess
    commands are get from docker history.
    """
    info = cli.inspect_image(ID)

    commands = []

    history = cli.history(ID)

    for item in history:
        if "/bin/sh -c #(nop) " in item["CreatedBy"]:
            commands.append(item["CreatedBy"][18:])
        else:
            commands.append(item["CreatedBy"])

    commands.reverse()
    return commands


def run(image1, image2, verbosity):
    """ Test history of the image.

    Adds one key to the output of the diff tool:
    "history" - unified_diff style changes in commands used to create
                the image
    """
    ID1, metadata1, output_dir1 = image1
    ID2, metadata2, output_dir2 = image2

    cli = docker.Client(base_url="unix://var/run/docker.sock")

    history1 = dockerfile_from_image(ID1, cli)
    history2 = dockerfile_from_image(ID2, cli)

    diff = [item for item in difflib.unified_diff(history1, history2, n=0) if not item.startswith(("+++","---","@@"))]

    return {"history":diff}
