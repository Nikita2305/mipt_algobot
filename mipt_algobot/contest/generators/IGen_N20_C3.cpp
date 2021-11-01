#include <iostream>
#include <time.h>

int main() {
    srand(time(0) + clock());
    int n = 1 + rand() % 20;
    for (int i = 0; i < n; i++) {
        std::cout << (char)('a' + rand() % 3);
    }
    std::cout << "$";
}
