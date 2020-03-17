echo "Clearing any output files"
del out1.txt
del out2.txt
del out3.txt
del out4.txt
echo "Running test program"
python3 Sudoku_BT.py input1.txt out1.txt
python3 Sudoku_BT.py input2.txt out2.txt
python3 Sudoku_BT.py input3.txt out3.txt
python3 Sudoku_BT.py input4.txt out4.txt
cls
echo "Checking for File Diffs"
fc out1.txt output1.txt
echo "Ran filecompare for input1"
PAUSE
cls
fc out2.txt output2.txt
echo "Ran filecompare for input2"
PAUSE
cls
fc out3.txt output3.txt
echo "Ran filecompare for input3"
PAUSE
cls
fc out4.txt output4.txt
echo "Ran filecompare for input4"
PAUSE
cls
echo "Test over"
PAUSE