echo off
echo -----Clearing any output files-----
del out1.txt
del out2.txt
del out3.txt
del out4.txt
PAUSE
echo -----Running test program-----
python Sudoku_ValueOrdering.py input1.txt out1.txt
python Sudoku_ValueOrdering.py input2.txt out2.txt
python Sudoku_ValueOrdering.py input3.txt out3.txt
python Sudoku_ValueOrdering.py input4.txt out4.txt
cls
echo -----Checking for Output Diffs-----
fc out1.txt output1.txt
if ERRORLEVEL 1 (
echo FAILED!
) else (
echo PASSED!
)
echo -----Ran filecompare for input1-----
PAUSE
fc out2.txt output2.txt
if ERRORLEVEL 1 (
echo FAILED!
) else (
echo PASSED!
)
echo -----Ran filecompare for input2-----
PAUSE
fc out3.txt output3.txt
if ERRORLEVEL 1 (
echo FAILED!
) else (
echo PASSED!
)
echo -----Ran filecompare for input3-----
PAUSE
fc out4.txt output4.txt
if ERRORLEVEL 1 (
echo FAILED!
) else (
echo PASSED!
)
echo -----Ran filecompare for input4-----
PAUSE
cls
echo -----Test over-----
PAUSE
