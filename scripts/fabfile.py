from fabric.api import local, settings, abort, run, cd, env, sudo, put, get
from fabric.contrib.console import confirm

import sys
import os
import time
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import *

env.hosts = ["192.168.1.1"]
env.user = ROOT_USER
env.password = ROOT_PASSWORD



def setup():
    pass









