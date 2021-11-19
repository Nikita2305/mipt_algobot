#include <iostream>
#include <string>
#include <fstream>

const int ERROR_CODE = 143;
const int FALSE_CODE = 144;
const int TRUE_CODE = 0;

int main(int argc, char* argv[]) {
    if (argc != 4) {
        return ERROR_CODE;
    }
    std::ifstream test(argv[1]);
    std::ifstream ok(argv[2]);
    std::ifstream user(argv[3]);
    if (!test.is_open()) {
        return ERROR_CODE;
    }
    if (!ok.is_open() && !user.is_open()) {
        return TRUE_CODE;
    } 
    if (!ok.is_open() || !user.is_open()) {
        return FALSE_CODE;
    }
    // Comparator starts here. Usage:
    // test >> var1;
    // ok >> var2;
    // user >> var3;
    std::string s1, s2;
    while (ok >> s1) {
        if (!(user >> s2)) {
            return FALSE_CODE;
        }
        if (s1 != s2) {
            return FALSE_CODE;
        }
    }
    char c;
    if (user >> c) {
        return FALSE_CODE;
    }
    return TRUE_CODE;
}
