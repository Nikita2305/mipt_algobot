#include <iostream>
#include <time.h>

int main() {
    srand(time(0) + clock());
    int L = 1 + rand() % 10;
    for (int i = 0; i < L; i++) {
        std::cout << (char)('a' + rand() % 2);
    }
    std::cout << std::endl;
    int N = 10;
    std::cout << N << std::endl;
    for (int i = 0; i < N; i++) {
        int l = 1 + rand() % 5;
        for (int j = 0; j < l; j++) {
            std::cout << (char)('a' + rand() % 2);
        }
        std::cout << std::endl;
    }
}
