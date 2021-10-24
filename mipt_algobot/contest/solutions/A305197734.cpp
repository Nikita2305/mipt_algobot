#include <iostream>
#include <vector>

std::vector<int> find_sufarr(std::string s) {
    s += "#";
    int n = s.length();   
    s += s;
    // let assume c[i] = class of i-th string in sort
    // thus c'[i] is obtained from {c[i], c[i + 2^k]}
    std::vector<int> c(n, -1), pos(n, 0);
    std::vector<int> count(26, 0);
    std::vector<int> v(n);
    for (int i = 0; i < n - 1; i++) {
        count[s[i] - 'a'] = 1;
    }
    for (int i = 1; i < 26; i++) {
        count[i] += count[i - 1];
    }
    for (int i = 0; i < n - 1; i++) {
        c[i] = count[s[i] - 'a'];
    }
    c[n - 1] = 0; 
    for (int len = 1; len < n; len <<= 1) { // len is the length of each part
        ////std::cout << "classes: ";
        for (int i = 0; i < n; i++) {
            //std::cout << c[i] << " ";
        }
        //std::cout << std::endl;
        std::vector<std::pair<int, int>> parts(n);
        std::vector<int> sort1(n);
        //std::cout << "parts: ";
        for (int i = 0; i < n; i++) {
            parts[i] = {c[i], c[(i + len) % n]};
            //std::cout << "{" << c[i] << " " << c[(i + len) % n] << "}" << " ";
        }
        //std::cout << std::endl;
        count.assign(n, 0);
        for (int i = 0; i < n; i++) {
            count[parts[i].second]++;
        }
        for (int i = 1; i < n; i++) {
            count[i] += count[i - 1];
        }
        for (int i = n - 1; i >= 0; i--) {
            sort1[--count[parts[i].second]] = i;
        }
        //std::cout << "sort1: ";
        for (int i = 0; i < n; i++) {
            //std::cout << sort1[i] << " ";
        }
        //std::cout << std::endl;
        count.assign(n, 0);
        for (int i = 0; i < n; i++) {
            count[parts[i].first]++;
        }
        for (int i = 1; i < n; i++) {
            count[i] += count[i - 1];
        }
        v.assign(n, 0);
        for (int i = n - 1; i >= 0; i--) { 
            pos[sort1[i]] = --count[parts[sort1[i]].first];
            v[pos[sort1[i]]] = sort1[i];
        }
        //std::cout << "pos: "; 
        for (int i = 0; i < n; i++) {
            //std::cout << pos[i] << " ";
        }
        //std::cout << std::endl << std::endl;
        int c_number = 0;
        c[v[0]] = c_number;
        for (int i = 1; i < n; i++) {
            if (parts[v[i]] != parts[v[i - 1]]) {
                c_number++;
            }
            c[v[i]] = c_number;
        }
    }
    v.erase(v.begin());
    return v;
}

main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(0);
    std::string s = "";
    std::cin >> s;
    std::vector<int> v = find_sufarr(s);
    for (int t : v) {
        std::cout << t + 1 << " ";
    }
}
