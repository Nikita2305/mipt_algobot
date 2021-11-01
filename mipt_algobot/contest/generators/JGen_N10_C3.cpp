#include <iostream>
#include <time.h>

int main() {
    clock();
    srand(10 * time(0) + clock());
    int n = rand() % 10 + 1;
    for (int i = 0; i < n; ++i)
        std::cout << static_cast<char>(rand() % 3 + 'a');
    std::cout << '\n';
    std::cout << (rand() % (n * (n + 1) / 2 + n)) % 100000 + 1 << '\n';
}
