for file in *.pdf; do
    echo $file

    filename="${file%%.*}"
    convert -density 300 $file -quality 100 -flatten "jpgs/"$filename".jpg"


done
