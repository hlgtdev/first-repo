root=$(pwd)
dir=../doc-api-v3

echo "[xmpg] $dir"

cd $root/$dir
xmpg || read

cd $root
dirs=$(find ../dependencies -maxdepth 2 -type f -name "*.py" | xargs dirname | uniq | sort)

for dir in $dirs
do
	clear
	echo "[xmpg] $dir"

	cd $root/$dir
	xmpg || read
done

cd $root
dirs=$(find . -maxdepth 3 -type f -name "*.py" | xargs dirname | uniq | sort)

for dir in $dirs
do
	clear
	echo "[xmpg] $dir"

	cd $root/$dir
	xmpg || read
done

cd $root
files=$(find .. -type f -name "*.svg" | sort)

if [[ -n $files ]];then
	firefox $files &
	echo
fi
