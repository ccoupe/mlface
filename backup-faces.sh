#!/bin/sh
#
# Rsync push /usr/local/lib/fcrecg/faces to bronco:/usr/local/lib/fcrecog/faces
# Caution: THIS RUNS as the user 'ccoupe' from his crontab
RSYNC="/usr/bin/rsync"
RSYNCOPTS="-e ssh --archive --update --delete --verbose "
EXCLUDEFILE="/home/ccoupe/backup/excludes.picts"
REMOTEPREFIX="buuf:"
$RSYNC $RSYNCOPTS --rsync-path=$RSYNC /usr/local/lib/fcrecog/known_faces/ \
bronco:/usr/local/lib/fcrecog/known_faces
