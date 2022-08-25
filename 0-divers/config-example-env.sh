export XMPG_HOME=~/projets/UTLDEV-prog-par-example/first-repo

bInstallClavierVirtuel=0

if [[ ! -d $XMPG_HOME ]];then
    export XMPG_HOME=/media/user/3ADA3A76DA3A2F0F/Users/jla/dev/first-repo
    bInstallClavierVirtuel=1
fi

echo $XMPG_HOME

sudo apt-get update
sudo apt-get install aptitude

if [[ $bInstallClavierVirtuel -eq 1 ]];then
    sudo aptitude install onboard
fi

sudo aptitude install git
sudo aptitude install default-jdk
sudo aptitude install graphviz
sudo aptitude install python3-pyqt5
sudo aptitude install python3-pip

sudo pip3 install readchar
sudo pip3 install pyyaml

aptitude show atom

if [[ $? -gt 0 ]];then
    if [[ ! -f ../../atom-amd64.deb ]];then
        wget https://github.com/atom/atom/releases/download/v1.54.0/atom-amd64.deb -O ../../atom-amd64.deb
    fi
    
    sudo gdebi ../../atom-amd64.deb
fi

sudo rm -f /usr/local/bin/xmpg
sudo ln -s $XMPG_HOME/xmprog/xmprog-runner.py /usr/local/bin/xmpg

git config --global user.name "hlgtdev"
git config --global user.email ""

