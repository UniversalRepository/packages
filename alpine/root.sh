#!/usr/bin/env bash
set -euo pipefail

work=$1
backend=$2
builder_uid=$3
builder_gid=$4
action=$5
recipe=${6:-}
key=${7:-}
root=$work/root

bootstrap=0
if [[ $action == setup ]]; then
    mkdir -p "$root/etc/apk/keys"
    cp "$backend"/etc/keys/*.rsa.pub "$root/etc/apk/keys/"
    if [[ ! -f $root/.urepo-bootstrap ]]; then
        printf '%s\n' \
            'https://dl-cdn.alpinelinux.org/alpine/edge/main' \
            'https://dl-cdn.alpinelinux.org/alpine/edge/community' > "$root/etc/apk/repositories"
        apk_env=(APK_CONFIG=/dev/null)
        if [[ -r /etc/pki/tls/openssl.cnf ]]; then
            apk_env+=(OPENSSL_CONF="$backend/etc/openssl.cnf")
        fi
        env "${apk_env[@]}" apk --root "$root" --arch x86_64 \
            --keys-dir etc/apk/keys --repositories-file "$root/etc/apk/repositories" \
            --initdb --no-cache --no-scripts add alpine-base
        bootstrap=1
    fi
else
    [[ -f $root/.urepo-bootstrap ]] || { printf '%s\n' 'error: Alpine build root is not prepared' >&2; exit 1; }
fi
mkdir -p "$root"/{dev,proc,build/{aports,packages,sources,backend},home/builder/.abuild,tmp/urepo-signing}
args=(--die-with-parent --bind "$root" / --dev-bind /dev /dev --proc /proc
    --ro-bind /etc/resolv.conf /etc/resolv.conf
    --ro-bind "$backend" /build/backend
    --bind "$work/config" /home/builder/.abuild)
for dir in aports packages sources; do
    args+=(--bind "$work/$dir" "/build/$dir")
done

if [[ $action == setup ]]; then
    bwrap "${args[@]}" --cap-add ALL \
        /bin/busybox env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/root \
        /bin/busybox sh -eu -s -- "$builder_uid" "$builder_gid" "$bootstrap" <<'SETUP'
printf '%s\n' \
    'https://dl-cdn.alpinelinux.org/alpine/edge/main' \
    'https://dl-cdn.alpinelinux.org/alpine/edge/community' \
    'https://dl-cdn.alpinelinux.org/alpine/edge/testing' > /etc/apk/repositories
if [ "$3" = 1 ]; then
    /bin/busybox --install -s
    apk --no-cache fix --reinstall --depends alpine-base
fi
apk --no-cache upgrade --available
apk --no-cache add alpine-sdk abuild-rootbld bash ca-certificates openssl python3 shadow setpriv
if ! id builder >/dev/null 2>&1; then
    groupadd -g "$2" builder
    useradd -u "$1" -g "$2" -G abuild -m -s /bin/bash builder
fi
[ "$(id -u builder)" = "$1" ] && [ "$(id -g builder)" = "$2" ]
chown builder:builder /home/builder
if [ -f /home/builder/.abuild/universalrepository.rsa.pub ]; then
    cp /home/builder/.abuild/universalrepository.rsa.pub /etc/apk/keys/
fi
SETUP
    touch "$root/.urepo-bootstrap"
    exit 0
fi

if [[ -n $key ]]; then
    args+=(--ro-bind "$key" /tmp/urepo-signing/universalrepository.rsa)
fi
bwrap "${args[@]}" --cap-add CAP_SETUID --cap-add CAP_SETGID \
    /usr/bin/env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/home/builder \
    /bin/setpriv --reuid="$builder_uid" --regid="$builder_gid" --init-groups \
    /bin/bash /build/backend/inside.sh "$action" "$recipe"
