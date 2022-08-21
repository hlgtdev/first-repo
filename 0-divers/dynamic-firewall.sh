FIELDS="
domain:
source:
netname:
organization:
orgname:
orgid:
descr:
address:
city:
stateprov:
postalcode:
country:
/ip/
"
TRUSTED_FILE=$1

if [[ -n $TRUSTED_FILE ]];then
    RE_TRUSTED=$(cat $TRUSTED_FILE | xargs -I{} printf "|{}")
    RE_TRUSTED=${RE_TRUSTED:1}
fi

echo $RE_TRUSTED

RE_FIELDS=$(echo $FIELDS | tr ' ' '|')

sudo -v

yes | sudo ufw reset || exit $?

sudo ufw logging on

sudo ufw default deny incoming
sudo ufw default deny outgoing
sudo ufw default deny routed

sudo ufw enable

# WHOIS
sudo ufw allow out 43/tcp

# DNS
sudo ufw allow out 53/udp

sudo ufw status verbose

while true
do
	stdOut=$(sudo dmesg --read-clear)
	echo "$stdOut" | awk '/ OUT=[a-z]+/ { print ">>> " $0 }'
	outIpsAndPorts=$(echo "$stdOut" | awk -F= '/ OUT=[a-z]+/ && / DST=/ {
			split($5, v1, " ")
			split($13, v2, " ")
			print v1[1] ":" v2[1]
		}' | sort | uniq)

	saveIpsAndPorts=""
	lookupSep=""
	
	for ipAndPort in $outIpsAndPorts
	do
		ip=$(echo $ipAndPort | cut -d: -f1)
		port=$(echo $ipAndPort | cut -d: -f2)
		
		lookupSep='"""'
		stdOut=$({
			sudo ufw status verbose
			echo $lookupSep
			echo " PORT $port"
			echo " IP $ip: $(sudo nslookup $ip)"
			echo "..."
			sudo ip route get $ip
			echo "..."
			whois $ip | grep -iE "$RE_FIELDS"
		} | tee /dev/tty)
		
		if [[ $(echo $saveIpsAndPorts | grep " $ipAndPort ") = "" ]];then
			if [[ $# -gt 1 ]] || [[ $port -ne 80 ]];then
                if [[ -z $TRUSTED_FILE ]] || [[ $(echo $stdOut | grep -E "$RE_TRUSTED") = "" ]];then
###				    printf "$stdOut\n$lookupSep\n" | zenity --text-info --title="AUTORISER $ip SUR LE PORT $port ?" --width=700 --height=700
###                 ret=$?
                    ret=1
                else
                    ret=0
				fi

				if [[ $ret -eq 0 ]];then
					sudo ufw allow out to $ip port $port
					sudo ufw status verbose
					
	echo "--- dyn-fw ---"
	sleep 1s

					saveIpsAndPorts="$saveIpsAndPorts $ipAndPort "
				fi
			fi
		fi
	done

	test -n "$lookupSep" && echo $lookupSep
done
