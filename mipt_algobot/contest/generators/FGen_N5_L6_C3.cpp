#include <iostream>
#include <time.h>

int main() {
    srand(time(0) + clock());
    int n = 1 + rand() % 5;
    std::cout << n << std::endl;
    for (int i = 0; i < n; i++) {
        int l = 1 + rand() % 6;
        while (l--) 
            std::cout << (char)('a' + rand() % 3);
        std::cout << "\n";
    }
}