from fabric.api import local, settings, abort, run, cd, env, sudo, put, get
from fabric.contrib.console import confirm

import sys
import os
import time
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import *

env.hosts = ["%s:%s" % ("192.168.1.3", SSH_PORT)]
env.user = ROOT_USER
env.password = ROOT_PASSWORD



def _set_user(subdomain):
    env.hosts = ["%s.glowedit.com:%s" % (subdomain, SSH_PORT)]
    env.user = DEPLOY_USER
    env.key_filename = "certs/deploy@%s.glowedit.com/id_rsa_deploy@%s.glowedit.com" % (subdomain, subdomain)


def install_docker(subdomain):

    _set_user(subdomain)
    #install docker
    sudo("apt-get update")
    sudo("apt-get install docker.io")
    sudo("ln -sf /usr/bin/docker.io /usr/local/bin/docker")
    sudo("sed -i '$acomplete -F _docker docker' /etc/bash_completion.d/docker.io")
    sudo("apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9")
    sudo (r'sh -c "echo deb https://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"')
    sudo("apt-get update")
    sudo("apt-get install -y lxc-docker")


def init_deploy_user(address, subdomain):

    env.hosts = [address]
    env.user = DEPLOY_USER
    env.password = DEPLOY_PASSWORD

    tunnel_port = TUNNEL_PORTS[subdomain]

    ## update apt and install autossh
    sudo("apt-get -y update", shell=False)
    sudo("apt-get -y upgrade", shell=False)
    sudo("apt-get -y install autossh", shell=False)

    ## copy localised deploy keys
    sudo("mkdir -p /home/deploy/.ssh", shell=False)
    put(_cert_path("deploy", subdomain), "/home/deploy/.ssh/", use_sudo=True)
    put(_cert_path("deploy", subdomain, public=True), "/home/deploy/.ssh/", use_sudo=True)

    ## put the private keys for deploy and local client_admin in deploy authorized_keys
    put("certs/deploy/id_rsa_deploy.pub", "/home/deploy/.ssh/authorized_keys", use_sudo=True)
    put(_cert_path("client_admin", subdomain, public=True), "/home/deploy/.ssh/tmp", use_sudo=True)
    sudo("cat /home/deploy/.ssh/tmp >> /home/deploy/.ssh/authorized_keys", shell=False)
    sudo("rm /home/deploy/.ssh/tmp", shell=False)

    ## correct ssh file permissions
    sudo("chown -R deploy:deploy /home/deploy/.ssh", shell=False)
    sudo("chmod 700 /home/deploy/.ssh", shell=False)
    sudo("chmod 600 /home/deploy/.ssh/authorized_keys", shell=False)

    ## change the ssh_conf to use only certs and allow only deploy access
    put("sshd_config", "/etc/ssh/sshd_config", use_sudo=True)

    ## add the reverse ssh service
    sudo("mkdir -p /home/deploy/tmp", shell=False)
    put("bouncer-tunnel.conf", "/home/deploy/tmp/", use_sudo=True)
    sudo("sed -i \"s/7000/%s/g\" /home/deploy/tmp/bouncer-tunnel.conf" % tunnel_port, shell=False)
    sudo("mv /home/deploy/tmp/bouncer-tunnel.conf /etc/init/bouncer-tunnel.conf", shell=False)

    ## set the domain name
    sudo("cat \"%s.glowedit.com\" > /etc/hostname" % subdomain)


def ensure_certs(subdomain):

    names = ["deploy", "flotsam", "client_admin"]

    for name in names:
        identity = "%s@%s.glowedit.com" % (name, subdomain)
        identity_dir = os.path.join("subdomains", subdomain, identity)
        dir_path = os.path.abspath(identity_dir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            cmd = "/usr/bin/ssh-keygen -v -t rsa -f %s/id_rsa_%s -C %s" % (dir_path, identity, identity)
            subprocess.call(cmd, shell=True)


def _cert_path(user, subdomain, public=False):

    path = "subdomains/%s/%s@%s.glowedit.com/id_rsa_%s@%s.glowedit.com" % (subdomain, user, subdomain, user, subdomain)

    if public:
        return "%s.pub" % path
    else:
        return path

def stop_dockers(subdomain=None):

    if subdomain:
        _set_user(subdomain)

    dockers = ["render_1", "render_2", "admin", "flask", "couchdb", "logspout"]
    for docker_name in dockers:
        sudo("docker stop %s" % docker_name)


def start_dockers(subdomain=None):

    if subdomain:
        _set_user(subdomain)

    dockers = ["logspout", "couchdb", "flask", "render_1", "render_2", "admin"]
    for docker_name in dockers:
        sudo("docker start %s" % docker_name)


def _delete_all_containers_and_images():

    sudo("docker rm $(docker ps -a -q)", shell=False)
    sudo("docker rmi $(docker images -q)", shell=False)


def _delete_non_data_containers(subdomain=None):

    if subdomain:
        _set_user(subdomain)

    stop_dockers()

    containers = ["render_1", "render_2", "admin", "flask", "couchdb", "logspout"]
    for container_name in containers:
        sudo("docker rm %s" % container_name)


def _clear_up_named_docker_images(subdomain):

    image_names = ["paulharter/river_render_worker:%s" % subdomain,
                   "paulharter/river_admin_worker:%s" % subdomain,
                   "paulharter/river_flask:%s" % subdomain,
                   "paulharter/river_app:latest"]

    for image_name in image_names:
        sudo("docker rmi %s" % image_name)


def _build_configured_images(subdomain):

    with cd ("/home/deploy/river"):
        sudo("docker build --no-cache=true -t=\"paulharter/river_flask:%s\" river_flask" % subdomain, shell=False)
        sudo("docker build --no-cache=true -t=\"paulharter/river_admin_worker:%s\" river_admin_worker" % subdomain, shell=False)
        sudo("docker build --no-cache=true -t=\"paulharter/river_render_worker:%s\" river_render_worker" % subdomain, shell=False)


def _create_all_non_data_containers(subdomain):

    # create couchdb container
    sudo("docker run -d --volumes-from couchdb_data --name couchdb -p 5984:5984 -e COUCHDB_USERNAME=admin -e COUCHDB_PASSWORD=Ubu3gMbp6tKLoiuVbMtLtEjsTMkGvEYi paulharter/river_couchdb", shell=False)

    # create web_app container
    sudo("docker run -d -p 80:5000 --link couchdb:couchdb --name flask paulharter/river_flask:%s" % subdomain, shell=False)

    # create admin worker container
    sudo("docker run -d --link couchdb:couchdb --name admin paulharter/river_admin_worker:%s" % subdomain, shell=False)

    # create render worker container
    sudo("docker run -d --link couchdb:couchdb --name render_1 paulharter/river_render_worker:%s" % subdomain, shell=False)

    # create another worker container
    sudo("docker run -d --link couchdb:couchdb --name render_2 paulharter/river_render_worker:%s" % subdomain, shell=False)

    #create logspout
    sudo("docker run -d --name logspout -h staging -v=/var/run/docker.sock:/tmp/docker.sock progrium/logspout dockersyslog://logs2.papertrailapp.com:44803", shell=False)


def _create_all_containers(subdomain):

    # create a data only container
    sudo("docker run -d -v /data --name couchdb_data dockerfile/ubuntu echo Data-only container for couchdb", shell=False)

    _create_all_non_data_containers(subdomain)


def provision(address, subdomain):
    ensure_certs(subdomain)
    init_deploy_user(address, subdomain)
    # install_docker(subdomain)
    # init(subdomain)



def init(subdomain):

    if subdomain:
        _set_user(subdomain)

    ## tear down
    stop_dockers()
    _delete_all_containers_and_images()

    ## build up
    update_docker_files()
    _build_configured_images(subdomain)
    _create_all_non_data_containers(subdomain)
    start_dockers()


def update(subdomain):

    if subdomain:
        _set_user(subdomain)

    ## tear down
    stop_dockers()
    _delete_non_data_containers()
    _clear_up_named_docker_images(subdomain)

    ## build up
    update_docker_files()
    _build_configured_images(subdomain)
    _create_all_non_data_containers(subdomain)
    start_dockers()











def update_docker_files(subdomain):

    if subdomain:
        _set_user(subdomain)

    sudo("apt-get install unzip")
    local('cd ../config/%s; zip -r ../../tmp/river.zip ./ -x "*.DS_Store"' % subdomain)
    sudo("mkdir -p /home/deploy/tmp")
    put("../tmp/river.zip", "/home/deploy/tmp/river.zip", use_sudo=True)
    sudo("rm -rf /home/deploy/river")

    with cd ('tmp'):
        sudo('unzip river.zip -d /home/deploy/river')
    sudo("rm  tmp/river.zip")
    local('rm ../tmp/river.zip')
    sudo("chown -R deploy:deploy /home/deploy/river")



def deploy_river_staging():
    pass


def _update_docker_files(config_name):

    sudo("apt-get install unzip")
    local('cd ../config/%s; zip -r ../../tmp/river.zip ./ -x "*.DS_Store"' % config_name)
    sudo("mkdir -p /home/deploy/tmp")
    put("../tmp/river.zip", "/home/deploy/tmp/river.zip", use_sudo=True)
    sudo("rm -rf /home/deploy/river")

    with cd ('tmp'):
        sudo('unzip river.zip -d /home/deploy/river')
    sudo("rm  tmp/river.zip")
    local('rm ../tmp/river.zip')
    sudo("chown -R deploy:deploy /home/deploy/river")

def deploy_sea():

    sudo("apt-get install unzip")
    local('cd ../config/%s; zip -r ../../tmp/sea.zip ./ -x "*.DS_Store"' % CONFIG_NAME)
    sudo("mkdir -p /home/deploy/tmp")
    put("../tmp/sea.zip", "/home/deploy/tmp/sea.zip", use_sudo=True)
    sudo("rm -rf /home/deploy/sea")

    with cd ('tmp'):
        sudo('unzip sea.zip -d /home/deploy/sea')
    sudo("rm  tmp/sea.zip")
    local('rm ../tmp/sea.zip')
    sudo("chown -R deploy:deploy /home/deploy/sea")





def setup_vb():



    setup()


def setup():

    config_name = "ravensbourne"

    config_file_path = os.path.join(BASE_DIR, "config", config_name)

    #upload some files

    sudo("mkdir -p ~config")




    return























