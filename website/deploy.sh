#!/bin/sh

cd _build/html
scp -P8471 -r . msworkbench@ms-workbench.de:
