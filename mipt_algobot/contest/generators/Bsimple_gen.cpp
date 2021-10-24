#include <iostream>
#include <time.h>

int main() {
    clock();
    srand(10 * time(0) + clock());
    int n = rand() % 20 + 5;
    for (int i = 0; i < n; ++i)
        std::cout << static_cast<char>(rand() % 26 + 97);
    std::cout << '\n';
    if (rand() % 10 == 0)
        std::cout << 1LL * 1234567890 * rand() + 1 << '\n';
    else if (rand() % 10 == 0)
        std::cout << n * (rand() % 10) + 1 << '\n';
    else
        std::cout << rand() % (n * n) + 1 << '\n';
}
