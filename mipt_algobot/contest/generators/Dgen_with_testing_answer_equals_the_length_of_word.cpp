#include <iostream>
#include <time.h>

int main() {
    clock();
    srand(10 * time(0) + clock());
    int n;
    if (rand() % 10 == 0) {
        std::cout << "abcdefgh\n";
        return 0;
    }
    if (rand() % 50 == 0)
        n = rand() % 20 + 5;
    else
        n = rand() % 10 + 5;
    for (int i = 0; i < n; ++i)
        std::cout << static_cast<char>(rand() % 26 + 97);
    std::cout << '\n';
}
