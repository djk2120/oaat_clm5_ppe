for i in {0..211}; do
    echo $i

    job='job'$i'.job'
    sed 's/num/'$i'/g' template.sh > $job
    qsub $job
        
done
