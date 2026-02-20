# Create orb vm
you're on mac with orbstack. use orb command to create ubuntu noble

after creation, ask user if they want to perform initial setup. If say yes, run the following setup

```
sudo apt update
sudo apt install git zsh openssh-server
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

curl -fsSL https://claude.ai/install.sh | bash

```
