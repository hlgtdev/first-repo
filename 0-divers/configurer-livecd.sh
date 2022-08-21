FIREFOX_PKG=firefox-esr
FIREFOX=firefox

UFW_BEFORE_RULES_FILE="/etc/ufw/before.rules"
ADDED_RULES_COMMENT="# REGLE AJOUTEE AUTOMATIQUEMENT"
OUTPUT_ICMP_ECHO_REQUEST="-A ufw-before-output -p icmp --icmp-type echo-request -j ACCEPT"

SCREEN_CHANNEL=$(xrandr | awk '/ connected / { print $1 }')
BRIGHTNESS=0.5
xrandr --output $SCREEN_CHANNEL --brightness $BRIGHTNESS

setxkbmap -layout fr
setxkbmap -print -verbose 10

if [[ "$(cat /sys/class/net/eno1/carrier)" = "1" ]];then
	nmcli radio wifi off
fi

# sudo -v

yes | sudo ufw reset # || exit $?

sudo apt-get update
sudo apt-get install -y ufw

# Autoriser le PING
if [[ -z $(sudo grep -e "$OUTPUT_ICMP_ECHO_REQUEST" $UFW_BEFORE_RULES_FILE) ]];then
	sudo sed -i "s/^COMMIT/$ADDED_RULES_COMMENT\n$OUTPUT_ICMP_ECHO_REQUEST\nCOMMIT/" $UFW_BEFORE_RULES_FILE
fi

sudo ufw logging on

sudo ufw default deny incoming
sudo ufw default deny routed

sudo ufw default allow outgoing

sudo ufw enable

### FIXME
sudo umount /dev/sda7
sudo mount -t ext4 -o ro,remount -force /dev/sda7 /data

sudo apt-get install -y dnsutils
sudo apt-get install -y wget
sudo apt-get install -y lsof
sudo apt-get install -y whois
sudo apt-get install -y gdebi

# wget https://go.skype.com/skypeforlinux-64.deb -O /tmp/skypeforlinux-64.deb
# yes | sudo gdebi /tmp/skypeforlinux-64.deb

sudo apt-get install -y $FIREFOX_PKG

#if [[ -z $(ps -eaf | grep "$FIREFOX" | grep -v "grep") ]];then
	$FIREFOX -private &
#fi

sudo ufw status verbose

