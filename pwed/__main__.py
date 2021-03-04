# -*- coding: utf-8 -*-
#  **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *              Viktor E. G. Bengtsson (viktor.bengtsson@mmk.su.se)   [2]
# *
# * [1] SciLifeLab, Stockholm University
# * [2] MMK, Stockholm University
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
import sys
import time
import argparse

import pwed


def main():
    parser = argparse.ArgumentParser()
    _add = parser.add_argument  # short notation

    # _add("projPath", metavar='PROJECT_NAME',
    #         help="Project database path.")
    #
    # _add("dbPath", metavar='DATABASE_PATH',
    #         help="Protocol database path.")
    #
    # _add("protId", type=int, metavar='PROTOCOL_ID',
    #         help="Protocol ID.")

    _add("-e", "--env",
         action='store_true',
         help="Print the existing environment")

    _add("--version",
         action="version",
         version=pwed.__version__)

    _add("project",
         nargs='?',
         default=None,
         help="Directly open the specified project ('last' or specified by name)")

    # _add("--wait_for", nargs='*', type=int, default=[],
    #         dest='waitProtIds', metavar='PROTOCOL_ID',
    #         help="List of protocol ids that should be not running "
    #              "(i.e, finished, aborted or failed) before this "
    #              "run will be executed.")

    args = parser.parse_args()

    if args.env:
        print("\nEnvironment:")
        print("   SCIPION_ED_USERDATA = ", pwed.Config.SCIPION_ED_USERDATA)
        print("   SCIPION_ED_TESTDATA = ", pwed.Config.SCIPION_ED_TESTDATA)

        print("\nExisting protocols:")
        plugins = pwed.Domain.getPlugins()
        for p in plugins:
            print("   ", p)

    if args.project:
        from pyworkflow.apps.pw_project import openProject
        openProject(args.project)

    # When no argument is passed, we should open the GUI
    if len(sys.argv) == 1:
        # Let's keep the import here to avoid GUI dependencies if not necessary
        from pyworkflow.gui.project import ProjectManagerWindow
        ProjectManagerWindow().show()


if __name__ == '__main__':
    main()
