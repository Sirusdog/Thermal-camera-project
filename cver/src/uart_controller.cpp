#include <iostream>
#include <stdio.h>
#include <vector>

using namespace std;

struct cmd {
    string cmdName;
    char byteData[23];
};

struct cmdSet {
    string setName;
    vector<cmd> subCommands;
};

cmdSet commands[] = {
    cmdSet(string("Pallet"), vector(
        cmd(string("Ough"), {"\x55","\x43","\x49","\x12","\x00","\x10","\x03","\x45","\x00","\x00","\x00","\x00","\x00","\x00","\x00","\x00","\x00","\x00","\x00","\x00","\x00","\x54","\x6D"})
    )),
};

void postCommand(int cmdID, int subCMDID) {
    cout << "Posting command" << "\n";
    return;
};

int main() {
    postCommand(1, 1);
    return 0;
}