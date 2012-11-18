#!/bin/bash
dir=/tmp/tail
i=0
while sleep 1
do
  for file in file-{0,1}
  do
    file=$dir/$file
    for c in 10;
    do
      echo -n $(((i++))) " " >> $file
      sleep 3
      echo $(((i++))) >> $file
    done
  done
done
