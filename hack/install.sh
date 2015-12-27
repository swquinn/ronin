#!/bin/sh
set -e

#: INSTALLATION INSTRUCTIONS
#: =========================
#:
#: This installation script was inspired by and derived from the
#: installation script that docker uses.
#:
#: This script is meant for quick & easy install via:
#:   'curl -sSL https://github.com/swquinn/ronin/ | sh'
#: or:
#:   'wget -qO- https://github.com/swquinn/ronin/ | sh'
#:
#: For test builds (ie. release candidates):
#:   'curl -sSL https://github.com/swquinn/ronin/ | sh'
#: or:
#:   'wget -qO- https://github.com/swquinn/ronin/ | sh'
#:
#: For experimental builds:
#:   'curl -sSL https://github.com/swquinn/ronin/ | sh'
#: or:
#:   'wget -qO- https://github.com/swquinn/ronin/ | sh'

#: The RELEASE_URL is the url that is used to get the install script
#: to install the release versions of ronin, and the repository is
#: the branch of ronin to clone and install from source.
RELEASE_URL=https://github.com/swquinn/ronin/
RELEASE_REPO=https://github.com/swquinn/ronin/

#: The TEST_URL is the url that is used to get the install script
#: to install the test versions of ronin, and the repository is
#: the branch of ronin to clone and install from source.
TEST_URL=https://github.com/swquinn/ronin/
TEST_REPO=https://github.com/swquinn/ronin/

#: The EXPERIMENTAL_URL is the url that is used to get the install script
#: to install the development/experimental versions of ronin, and the repository is
#: the branch of ronin to clone and install from source.
EXPERIMENTAL_URL=https://github.com/swquinn/ronin/
EXPERIMENTAL_REPO=https://github.com/swquinn/ronin/

command_exists() {
  command -v "$@" > /dev/null 2>&1
}

# Check if this is a forked Linux distro
check_forked() {
	# Check for lsb_release command existence, it usually exists in forked distros
	if command_exists lsb_release; then
		# Check if the `-u` option is supported
		set +e
		lsb_release -a -u > /dev/null 2>&1
		lsb_release_exit_code=$?
		set -e

		# Check if the command has exited successfully, it means we're in a forked distro
		if [ "$lsb_release_exit_code" = "0" ]; then
			# Print info about current distro
			cat <<-EOF
			You're using '$lsb_dist' version '$dist_version'.
			EOF

			# Get the upstream release info
			lsb_dist=$(lsb_release -a -u 2>&1 | tr '[:upper:]' '[:lower:]' | grep -E 'id' | cut -d ':' -f 2 | tr -d '[[:space:]]')
			dist_version=$(lsb_release -a -u 2>&1 | tr '[:upper:]' '[:lower:]' | grep -E 'codename' | cut -d ':' -f 2 | tr -d '[[:space:]]')

			# Print info about upstream distro
			cat <<-EOF
			Upstream release is '$lsb_dist' version '$dist_version'.
			EOF
		fi
	fi
}

echo_ronin_as_nonroot() {
  if command_exists python ; then
    (
      set -x
      $sh_c 'python --version'
    ) || true
  fi
  your_user=your-user
  [ "$user" != 'root' ] && your_user="$user"
  # intentionally mixed spaces and tabs here -- tabs are stripped by "<<-EOF", spaces are kept in the output
  cat <<-EOF

  If you would like to use Ronin as a non-root user, you should now consider
  adding your user to the "ronin" group with something like:

    sudo usermod -aG ronin $your_user

  Remember that you will have to log out and back in for this to take effect!

EOF
}

do_install() {
  if ! command_exists python; then
    cat >&2 <<-'EOF'
      Error: this installer requires Python be installed on your system.
      We are unable to find the "python" interpreter to install Ronin.
EOF
      exit 1
  fi

  user="$(id -un 2>/dev/null || true)"

  sh_c='sh -c'
  if [ "$user" != 'root' ]; then
    if command_exists sudo; then
      sh_c='sudo -E sh -c'
    elif command_exists su; then
      sh_c='su -c'
    else
      cat >&2 <<-'EOF'
      Error: this installer needs the ability to run commands as root.
      We are unable to find either "sudo" or "su" available to make this happen.
EOF
      exit 1
    fi
  fi

  curl=''
  if command_exists curl; then
    curl='curl -sSL'
  elif command_exists wget; then
    curl='wget -qO-'
  elif command_exists busybox && busybox --list-modules | grep -q wget; then
    curl='busybox wget -qO-'
  fi

  # check to see which repo they are trying to install from
  repo=$RELEASE_REPO
  if [ $TEST_URL = "$url" ]; then
    repo=$TEST_REPO
  elif [ $EXPERIMENTAL_URL = "$url" ]; then
    repo=$EXPERIMENTAL_REPO
  fi

  # perform some very rudimentary platform detection
  lsb_dist=''
  dist_version=''
  if command_exists lsb_release; then
    lsb_dist="$(lsb_release -si)"
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/lsb-release ]; then
    lsb_dist="$(. /etc/lsb-release && echo "$DISTRIB_ID")"
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/debian_version ]; then
    lsb_dist='debian'
  fi
  if [ -z "$lsb_dist" ] && [ -r /etc/os-release ]; then
    lsb_dist="$(. /etc/os-release && echo "$ID")"
  fi

  lsb_dist="$(echo "$lsb_dist" | tr '[:upper:]' '[:lower:]')"

  case "$lsb_dist" in

    ubuntu)
      if command_exists lsb_release; then
        dist_version="$(lsb_release --codename | cut -f2)"
      fi
      if [ -z "$dist_version" ] && [ -r /etc/lsb-release ]; then
        dist_version="$(. /etc/lsb-release && echo "$DISTRIB_CODENAME")"
      fi
    ;;

    debian)
      dist_version="$(cat /etc/debian_version | sed 's/\/.*//' | sed 's/\..*//')"
      case "$dist_version" in
        8)
          dist_version="jessie"
        ;;
        7)
          dist_version="wheezy"
        ;;
      esac
    ;;

    *)
      if command_exists lsb_release; then
        dist_version="$(lsb_release --codename | cut -f2)"
      fi
      if [ -z "$dist_version" ] && [ -r /etc/os-release ]; then
        dist_version="$(. /etc/os-release && echo "$VERSION_ID")"
      fi
    ;;


  esac

  # Check if this is a forked Linux distro
  check_forked

  # Run setup for each distro accordingly
  case "$lsb_dist" in

    ubuntu|debian)
      export DEBIAN_FRONTEND=noninteractive

      did_apt_get_update=
      apt_get_update() {
        if [ -z "$did_apt_get_update" ]; then
          ( set -x; $sh_c 'sleep 3; apt-get update' )
          did_apt_get_update=1
        fi
      }

      # install git if its missing otherwise ronin will fail to download!
      if ! command_exists git; then
        apt_get_update
        ( set -x; $sh_c "sleep 3; apt-get install -y -q git" )
      fi

      if [ ! -e /usr/lib/apt/methods/https ]; then
        apt_get_update
        ( set -x; $sh_c 'sleep 3; apt-get install -y -q apt-transport-https ca-certificates' )
      fi
      if [ -z "$curl" ]; then
        apt_get_update
        ( set -x; $sh_c 'sleep 3; apt-get install -y -q curl ca-certificates' )
        curl='curl -sSL'
      fi
      (
      set -x
      $sh_c "mkdir -p /tmp/ronin"
      $sh_c "git clone $repo ronin_source"
      $sh_c 'sleep 3; python setup.py install'
      )
      echo_ronin_as_nonroot
      exit 0
      ;;
  esac

  cat >&2 <<-'EOF'

    Either your platform is not easily detectable, or is not supported by this
    installer script (yet - PRs welcome! [hack/install.sh]). Please visit the
    following URL for more detailed installation instructions:

      https://github.com/swquinn/ronin/

EOF
  exit 1
}

# wrapped up in a function so that we have some protection against only getting
# half the file during "curl | sh"
do_install
