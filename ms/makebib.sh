grep citation ms.aux | sed 's/citation//g' | tr -d '\\{}' | sort | uniq > cites.txt

d='/Users/kennedy/projects/references/refs/'
:> refs.bib
while read c; do
    file=$d$c".bib"
    if [ -f $file ]; then
	cat $file >> refs.bib
	echo -en '\n' >> refs.bib
    else
	echo "missing bib: "$c
    fi
done < cites.txt
    
