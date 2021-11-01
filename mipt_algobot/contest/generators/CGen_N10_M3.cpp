#include <iostream>
#include <time.h>

int main() {
    srand(time(0) + clock());
    int n = 1 + rand() % 10, m = 1 + rand() % 3;
    std::cout << n << " " << m << std::endl;
    for (int i = 0; i < n; i++) {
        std::cout << 1 + rand() % m << " ";
    }
}
