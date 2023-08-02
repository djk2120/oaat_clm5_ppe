grep citation ms.aux | sed 's/citation//g' | tr -d '\\{}' | sort | uniq > cites.txt

d='/Users/djk2120/projects/references/refs/'
:> refs.bib
while read c; do
    file=$d$c".bib"
    echo $file
    if [ -f $file ]; then
	cat $file >> refs.bib
	echo -en '\n' >> refs.bib
    else
	echo "missing bib: "$c
    fi
done < cites.txt
    
