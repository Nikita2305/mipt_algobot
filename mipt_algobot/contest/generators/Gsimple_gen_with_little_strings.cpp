#include <iostream>
#include <time.h>

int main() {
    clock();
    srand(10 * time(0) + clock());
    int n = 15;
    for (int i = 0; i < n; ++i) {
        if (rand() % 2) {
            std::cout << "A ";
            int m = rand() % 4 + 4;
            for (int j = 0; j < m; ++j)
                std::cout << static_cast<char>(rand() % 2 ? 65 + rand() % 6 : 97 + rand() % 6);
            std::cout << '\n';
        } else {
            std::cout << "? ";
            int m = rand() % 4 + 1;
            for (int j = 0; j < m; ++j)
                std::cout << static_cast<char>(rand() % 2 ? 65 + rand() % 6 : 97 + rand() % 6);
            std::cout << '\n';
        }
    }
}
