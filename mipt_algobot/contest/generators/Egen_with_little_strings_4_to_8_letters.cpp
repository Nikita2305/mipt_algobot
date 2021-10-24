#include <iostream>
#include <time.h>

int main() {
    clock();
    srand(10 * time(0) + clock());
    int n = rand() % 5 + 4;
    for (int i = 0; i < n; ++i)
        std::cout << static_cast<char>(rand() % 26 + 97);
    std::cout << '\n';
}
