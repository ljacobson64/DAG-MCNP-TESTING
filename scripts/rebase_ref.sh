#!/bin/bash

cd ../Dagmc

for i in $(seq -f "%02g" 1 15); do
  cp results/$i/test$i.o cases/$i/ref.dag.out
  cp results/$i/test$i.m cases/$i/ref.dag.mctal
done

cd ../scripts
