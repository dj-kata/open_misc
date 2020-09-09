for x in "$@"
do
	#./enc.py $x --acopy --vbitrate 2  --rm
	./enc.py $x --acopy --vbitrate 2
	echo $x
done
