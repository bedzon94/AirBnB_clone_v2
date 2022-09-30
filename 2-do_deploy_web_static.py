#!/usr/bin/python3
"""Generates a .tgz archive from the
contents of the web_static folder
Distributes an archive to a web server"""

from fabric.operations import local, run, put, sudo
from datetime import datetime
import os
from fabric.api import env
import re


env.hosts = ['44.211.26.34', '44.192.114.202']
env.user = "ubuntu"
env.key_filename = '~/.ssh/id_rsa.pub'


def do_pack():
    """Function to compress files in an archive"""
    local("mkdir -p versions")
    result = local("tar -cvzf versions/web_static_{}.tgz web_static"
                   .format(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")),
                   capture=True)
    if result.failed:
        return None
    return result


def do_deploy(archive_path):
    """Function to distribute an archive to a server"""
    if not os.path.exists(archive_path):
        return False
    rex = r'^versions/(\S+).tgz'
    match = re.search(rex, archive_path)
    filename = match.group(1)
    res = put(archive_path, "/tmp/{}.tgz".format(filename))
    if res.failed:
        return False
    res = sudo("mkdir -p /data/web_static/releases/{}/".format(filename))
    if res.failed:
        return False
    res = sudo("tar -xzf /tmp/{}.tgz -C /data/web_static/releases/{}/"
              .format(filename, filename))
    if res.failed:
        return False
    res = sudo("rm /tmp/{}.tgz".format(filename))
    if res.failed:
        return False
    res = sudo("mv /data/web_static/releases/{}"
              "/web_static/* /data/web_static/releases/{}/"
              .format(filename, filename))
    if res.failed:
        return False
    res = sudo("rm -rf /data/web_static/releases/{}/web_static"
              .format(filename))
    if res.failed:
        return False
    res = sudo("rm -rf /data/web_static/current")
    if res.failed:
        return False
    res = sudo("ln -s /data/web_static/releases/{}/ /data/web_static/current"
              .format(filename))
    if res.failed:
        return False
    print('New version deployed!')
    return True
