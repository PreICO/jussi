#!/usr/bin/env sh

SERVICE=jussi

[ ! -z ${JUSSI_USER} ] || JUSSI_USER=${SERVICE}d
[ ! -z ${JUSSI_HOME} ] || JUSSI_HOME=/usr/local/${SERVICE}d
[ ! -z ${JUSSI_PORT} ] || JUSSI_PORT=9000
[ ! -z ${JUSSI_DOCKER_HOST} ] || JUSSI_DOCKER_HOST=unix:///var/run/docker.sock

WORKTREE=`dirname \`realpath ${0}\``
SERVICE_REPO=${SUDO_USER}/${PROJECT}_${SERVICE}
STAGE0=${SERVICE_REPO}_stage0
JUSSI_GIT_REV=`cd ${WORKTREE} && git rev-parse HEAD`
STAGE1=${SERVICE_REPO}:${JUSSI_GIT_REV}
STAGE_LATEST=${SERVICE_REPO}:latest
DIRTY=`cd ${WORKTREE} && git status -s`

mkdir -p ${WORKTREE}/.local && \
chown \
    -R \
    ${SUDO_UID}:${SUDO_GID} \
    ${WORKTREE}/.local && \
([ -z "${DIRTY}" ] && buildah inspect ${STAGE1} > /dev/null 2> /dev/null || \
 (buildah inspect ${STAGE0} > /dev/null 2> /dev/null || \
  buildah from \
      --name ${STAGE0} \
      ubuntu:bionic) && \
 buildah config \
     -u root \
     --workingdir ${WORKTREE} \
     ${STAGE0} && \
 buildah run \
     ${STAGE0} \
     /usr/bin/env \
         -u USER \
         -u HOME \
         sh -c -- \
            "apt update && \
             apt upgrade -y && \
             apt install -y python3-pip" && \
 buildah run \
     --user ${SUDO_UID}:${SUDO_GID} \
     -v ${WORKTREE}:/usr/src/${SERVICE}:ro \
     -v ${WORKTREE}/.local:/usr/src/${SERVICE}/.local \
     ${STAGE0} \
     /usr/bin/env \
         -u USER \
         LANG=C.UTF-8 \
         LC_ALL=C.UTF-8 \
         HOME=/usr/src/${SERVICE} \
         PATH=/usr/src/${SERVICE}/.local/sbin:/usr/src/${SERVICE}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
         sh -c -- \
            "cd /usr/src/${SERVICE} && \
             pip3 install \
                 -r requirements.txt \
                 -r requirements-dev.txt &&
             find ./.local/lib -type d -exec chmod 755 {} \;" && \
 buildah run \
     -v ${WORKTREE}:/usr/src/${SERVICE}:ro \
     ${STAGE0} \
     /usr/bin/env \
         -u USER \
         -u HOME \
         sh -c -- \
            "adduser \
                 --system \
                 --home ${JUSSI_HOME} \
                 --shell /bin/bash \
                 --group \
                 --disabled-password \
                 ${JUSSI_USER} && \
             rm -rf ${JUSSI_HOME} && \
             cp \
                 -PRT \
                 /usr/src/${SERVICE} \
                 ${JUSSI_HOME}" && \
 buildah config \
     -e LANG=C.UTF-8 \
     -e LC_ALL=C.UTF-8 \
     -e USER=${JUSSI_USER} \
     -e HOME=${JUSSI_HOME} \
     -e JUSSI_SERVER_PORT=${JUSSI_PORT} \
     --cmd "python3 \
            -m jussi.serve \
            --source_commit ${JUSSI_GIT_REV} \
            --docker_tag ${JUSSI_GIT_REV} \
            --upstream_config_file ${JUSSI_HOME}/config.json" \
     -p ${JUSSI_PORT} \
     -u ${JUSSI_USER} \
     --workingdir ${JUSSI_HOME} \
     ${STAGE0} && \
 buildah commit \
     ${STAGE0} \
     ${STAGE1} &&
 buildah tag \
     ${STAGE1} \
     ${STAGE_LATEST} &&
 buildah push \
     --dest-daemon-host ${JUSSI_DOCKER_HOST} \
     ${STAGE1} \
     docker-daemon:${STAGE1} &&
 docker \
     -H ${JUSSI_DOCKER_HOST} \
     tag \
         ${STAGE1} \
         ${STAGE_LATEST})
