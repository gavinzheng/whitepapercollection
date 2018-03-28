#!/bin/bash

# 1. Set the OPENEDX_RELEASE variable:
export OPENEDX_RELEASE=open-release/ficus.master
# 2. Bootstrap the Ansible installation:
wget https://raw.githubusercontent.com/edx/configuration/$OPENEDX_RELEASE/util/install/ansible-bootstrap.sh -O - | sudo bash
# 3. (Optional) If this is a new installation, randomize the passwords:
wget https://raw.githubusercontent.com/edx/configuration/$OPENEDX_RELEASE/util/install/generate-passwords.sh -O - | bash
# 4. Install Open edX:
wget https://raw.githubusercontent.com/edx/configuration/$OPENEDX_RELEASE/util/install/sandbox.sh -O - | bash

