#!/bin/sh
./run_tests.sh --tests=testTable.py $*
./run_tests.sh --tests=regTestTable.py $*
./run_tests.sh --tests=testElements.py $*
./run_tests.sh --tests=testExpressionTree.py $*
./run_tests.sh --tests=testMSTypes.py $*
./run_tests.sh --tests=testUtilityNamespaces.py $*
python  << EOF
import mass
import abundance
import elements
import ms
import batches
EOF
