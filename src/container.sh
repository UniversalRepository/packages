container_build() {
    local engine candidate uid= gid= image name value key
    local published=${UREPO_BUILDER_IMAGE:-ghcr.io/universalrepository/builder:latest}
    local -a build_args=() run_args=() engines=()

    validate_targets "$@"
    [[ -f $UREPO_ROOT/Containerfile ]] || die 'missing Containerfile'

    if [[ ${CI:-false} =~ ^(false|0)?$ && ${GITHUB_ACTIONS:-false} != true ]]; then
        uid=$(id -u)
        gid=$(id -g)
        (( uid != 0 )) || die 'run container builds as your normal user, not root'
        build_args+=(--build-arg "BUILDER_UID=$uid" --build-arg "BUILDER_GID=$gid")
    fi

    engine=
    read -r -a engines <<< "${UREPO_CONTAINER_ENGINE:-podman docker}"
    for candidate in "${engines[@]}"; do
        case $candidate in
            podman|docker) ;;
            *) die 'UREPO_CONTAINER_ENGINE must be podman or docker' ;;
        esac
        command -v "$candidate" >/dev/null 2>&1 || continue
        "$candidate" info >/dev/null 2>&1 || continue
        if [[ $candidate == docker && -n $uid ]]; then
            value=$(docker info --format '{{json .SecurityOptions}}') || continue
            if [[ $value == *rootless* ]]; then
                warn 'rootless Docker cannot preserve non-root builder ownership, use Podman or rooted Docker'
                continue
            fi
        fi
        engine=$candidate
        break
    done
    [[ -n $engine ]] || die 'no usable container engine, configure Podman or Docker access'

    run_args=(--rm --privileged --user 0 --workdir /workspace
        --volume "$UREPO_ROOT:/workspace" --entrypoint /bin/bash)
    if [[ $engine == podman ]]; then
        [[ -z $uid ]] || run_args+=(--userns=keep-id --volume /dev:/dev)
    else
        run_args+=(--userns=host)
    fi
    [[ ! -t 0 ]] || run_args+=(--interactive)
    [[ ! -t 0 || ! -t 1 ]] || run_args+=(--tty)

    for name in UREPO_VOID_SIGNED_BY UREPO_VOID_XBPS_ARGS UREPO_ARCH_ARCH UREPO_RPM_ARCH UREPO_SIGN_NAME XBPS_ARCH XBPS_TARGET_ARCH NO_COLOR TERM; do
        [[ ! ${!name+x} ]] || run_args+=(--env "$name=${!name}")
    done
    for name in UREPO_VOID_SIGN_KEY UREPO_GPG_SIGN_KEY; do
        [[ ${!name+x} ]] || continue
        key=${!name}
        [[ $key == /* ]] || key=$PWD/$key
        [[ -f $key && -r $key ]] || die "cannot read signing key: $key"
        run_args+=(--volume "$key:/run/urepo/$name:ro" --env "$name=/run/urepo/$name")
    done

    if [[ $engine == docker && ! -f $UREPO_ROOT/.dockerignore ]]; then
        [[ -f $UREPO_ROOT/.containerignore ]] || die 'missing .dockerignore and .containerignore'
        cp -- "$UREPO_ROOT/.containerignore" "$UREPO_ROOT/.dockerignore"
    fi

    image=localhost/urepo-builder:local-${uid:-default}-${gid:-default}
    info "Building local builder image with $engine"
    if ! "$engine" build --file "$UREPO_ROOT/Containerfile" --tag "$image" \
        "${build_args[@]}" "$UREPO_ROOT"; then
        warn "local image build failed, pulling $published"
        "$engine" pull "$published" || die "cannot pull builder image: $published"
        image=$published
    fi

    info "Building packages with $engine ($image)"
    "$engine" run "${run_args[@]}" "$image" -euo pipefail -c '
        uid=$1
        gid=$2
        shift 2
        if [[ -n $uid ]]; then
            if [[ $(id -u builder) != "$uid" || $(id -g builder) != "$gid" ]]; then
                groupmod --non-unique --gid "$gid" builder
                usermod --non-unique --uid "$uid" --gid "$gid" builder
                chown -R "$uid:$gid" /home/builder
            fi
        fi
        exec runuser -u builder -- ./urepo build "$@"
    ' urepo-container "$uid" "$gid" "$@"
}
