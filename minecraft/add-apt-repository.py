#! /usr/bin/python3

from __future__ import print_function

import io
import os
import sys
import gettext
import locale

from softwareproperties.SoftwareProperties import SoftwareProperties, shortcut_handler
from softwareproperties.shortcuts import ShortcutException
from softwareproperties.ppa import DEFAULT_KEYSERVER
import aptsources
from aptsources.sourceslist import SourceEntry
from optparse import OptionParser
from gettext import gettext as _

if __name__ == "__main__":
    # Force encoding to UTF-8 even in non-UTF-8 locales.
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), encoding="UTF-8", line_buffering=True)

    try:
        locale.setlocale(locale.LC_ALL, "")
    except:
        pass
    gettext.textdomain("software-properties")
    usage = """Usage: %prog <sourceline>

%prog is a script for adding apt sources.list entries.
It can be used to add any repository and also provides a shorthand
syntax for adding a Launchpad PPA (Personal Package Archive)
repository.

<sourceline> - The apt repository source line to add. This is one of:
  a complete apt line in quotes,
  a repo url and areas in quotes (areas defaults to 'main')
  a PPA shortcut.
  a distro component

  Examples:
    apt-add-repository 'deb http://myserver/path/to/repo stable myrepo'
    apt-add-repository 'http://myserver/path/to/repo myrepo'
    apt-add-repository 'https://packages.medibuntu.org free non-free'
    apt-add-repository http://extras.ubuntu.com/ubuntu
    apt-add-repository ppa:user/repository
    apt-add-repository multiverse

If --remove is given the tool will remove the given sourceline from your
sources.list
"""
    parser = OptionParser(usage)
    # FIXME: provide a --sources-list-file= option that
    #        puts the line into a specific file in sources.list.d
    parser.add_option ("-m", "--massive-debug", action="store_true",
        dest="massive_debug", default=False,
        help=_("Print a lot of debug information to the command line"))
    parser.add_option("-r", "--remove", action="store_true",
        dest="remove", default=False,
        help=_("remove repository from sources.list.d directory"))
    parser.add_option("-k", "--keyserver",
        dest="keyserver", default=DEFAULT_KEYSERVER,
        help=_("URL of keyserver. Default: %default"))
    parser.add_option("-s", "--enable-source", action="store_true",
        dest="enable_source", default=False,
        help=_("Allow downloading of the source packages from the repository"))
    parser.add_option("-y", "--yes", action="store_true",
        dest="assume_yes", default=False,
        help=_("Assume yes to all queries"))
    (options, args) = parser.parse_args()

    if os.geteuid() != 0:
        print(_("Error: must run as root"))
        sys.exit(1)

    if len(args) == 0:
        print(_("Error: need a repository as argument"))
        sys.exit(1)
    elif len(args) > 1:
        print(_("Error: need a single repository as argument"))
        sys.exit(1)

    # force new ppa file to be 644 (LP: #399709)
    os.umask(0o022)

    # get the line
    line = args[0]

    # add it
    sp = SoftwareProperties(options=options)
    distro = aptsources.distro.get_distro()
    distro.get_sources(sp.sourceslist)

    # check if its a component that should be added/removed
    components = [comp.name for comp in distro.source_template.components]
    if line in components:
        if options.remove:
            if line in distro.enabled_comps:
                distro.disable_component(line)
                print(_("'%s' distribution component disabled for all sources.") % line)
            else:
                print(_("'%s' distribution component is already disabled for all sources.") % line)
                sys.exit(0)
        else:
            if line not in distro.enabled_comps:
                distro.enable_component(line)
                print(_("'%s' distribution component enabled for all sources.") % line)
            else:
                print(_("'%s' distribution component is already enabled for all sources.") % line)
                sys.exit(0)
        sp.sourceslist.save()
        sys.exit(0)

    # this wasn't a component name ('multiverse', 'backports'), so its either
    # a actual line to be added or a shortcut.
    try:
        shortcut = shortcut_handler(line)
    except ShortcutException as e:
        print(e)
        sys.exit(1)

    # display more information about the shortcut / ppa info
    if not options.assume_yes and shortcut.should_confirm():
        try:
            info = shortcut.info()
        except ShortcutException as e:
            print(e)
            sys.exit(1)

        print(" %s" % (info["description"] or ""))
        print(_(" More info: %s") % str(info["web_link"]))
        if (sys.stdin.isatty() and
            not "FORCE_ADD_APT_REPOSITORY" in os.environ):
            if options.remove:
                print(_("Press [ENTER] to continue or ctrl-c to cancel removing it"))
            else:
                print(_("Press [ENTER] to continue or ctrl-c to cancel adding it"))
            sys.stdin.readline()


    if options.remove:
        try:
            (line, file) = shortcut.expand(sp.distro.codename)
        except ShortcutException as e:
            print(e)
            sys.exit(1)
        deb_line = sp.expand_http_line(line)
        debsrc_line = 'deb-src' + deb_line[3:]
        deb_entry = SourceEntry(deb_line, file)
        debsrc_entry = SourceEntry(debsrc_line, file)
        try:
            sp.remove_source(deb_entry)
        except ValueError:
            print(_("Error: '%s' doesn't exist in a sourcelist file") % deb_line)
        try:
            sp.remove_source(debsrc_entry)
        except ValueError:
            print(_("Error: '%s' doesn't exist in a sourcelist file") % debsrc_line)

    else:
        try:
            if not sp.add_source_from_shortcut(shortcut, options.enable_source):
                print(_("Error: '%s' invalid") % line)
                sys.exit(1)
        except ShortcutException as e:
            print(e)
            sys.exit(1)

        sp.sourceslist.save()