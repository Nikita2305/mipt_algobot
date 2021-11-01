#include <iostream>
#include <time.h>

int main() {
    clock();
    srand(10 * time(0) + clock());
    int n = rand() % 10 + 1;
    for (int i = 0; i < n; ++i)
        std::cout << (char)('a' + rand() % 3);
    std::cout << '\n';
    std::cout << rand() % (n * (n + 1) / 2 + n) + 1 << '\n';
}
