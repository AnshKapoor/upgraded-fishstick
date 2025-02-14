#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev

curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

if [ -f ~/.bash_profile ]; then
  FILE=~/.bash_profile
else
  FILE=~/.profile
fi

if ! grep 'pyenv' $FILE >/dev/null; then
cat >>$FILE <<EOF

export PATH="~/.pyenv/bin:\$PATH"
eval "\$(pyenv init -)"
eval "\$(pyenv virtualenv-init -)"
EOF
fi

if [ -f ~/.bashrc ]; then
FILE=~/.bashrc
if ! grep 'pyenv' $FILE >/dev/null; then
cat >>$FILE <<EOF

export PATH="~/.pyenv/bin:\$PATH"
eval "\$(pyenv init -)"
eval "\$(pyenv virtualenv-init -)"
EOF
fi
fi

export PATH="/home/ubuntu/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.6.1
pyenv local 3.6.1
cd -
