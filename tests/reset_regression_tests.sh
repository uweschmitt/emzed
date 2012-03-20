#!/bin/sh
for U in *.is; do
    cp $U ${U%.is}.tobe
done
