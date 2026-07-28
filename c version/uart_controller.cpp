#include <iostream>
#include <stdio.h>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

struct cmd {
    string cmdName;
    char[] byteData;
}

struct cmdSet {
    string setName;
    cmd[] subCommands;
}

cmdSet[] commands = {
    cmdSet()
}

void postCommand(int cmdID, int subCMDID) {
    cout << "Posting command"



}