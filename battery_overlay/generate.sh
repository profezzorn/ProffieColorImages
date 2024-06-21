#!/bin/sh

for size in 160x128 160x80 320x240
do
  cpqoi batt${size}.pqoiml >batt_${size}.pqf
done
