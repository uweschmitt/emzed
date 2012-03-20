#!/bin/sh
./run_tests.sh --tests=testExpressions.py $*
./run_tests.sh --tests=testTable.py $*
./run_tests.sh --tests=testExpressions.py $*
./run_tests.sh --tests=testTable2.py $*
./run_tests.sh --tests=testMSTypes.py $*
./run_tests.sh --tests=testTableParsers.py $*
./run_tests.sh --tests=regTestTable.py $*
./run_tests.sh --tests=testMsIntegrate.py $*
./run_tests.sh --tests=testMzAlign.py $*
./run_tests.sh --tests=testAnova.py $*
./run_tests.sh --tests=testIDGen.py $*
./run_tests.sh --tests=testTableExplorerModel.py $*
./run_tests.sh --tests=testElements.py $*
./run_tests.sh --tests=testUtilityNamespaces.py $*
./run_tests.sh --tests=testPeakIntegration.py $*
./run_tests.sh --tests=testCSVParsing.py $*
python  << EOF
import mass
import abundance
import elements
import ms
import batches
EOF
