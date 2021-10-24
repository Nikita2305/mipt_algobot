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
        std::vector<std::pair<int, int>> parts(n);
        std::vector<int> sort1(n);
        for (int i = 0; i < n; i++) {
            parts[i] = {c[i], c[(i + len) % n]};
        }
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

std::vector<int> find_lcp(const std::string& s, const std::vector<int>& sufarr) {
    int n = s.length();
    std::vector<int> pos(n);
    for (int i = 0; i < n; i++) {
        pos[sufarr[i]] = i;
    }
    int l = 0;
    std::vector<int> lcp(n - 1);
    for (int w = 0; w < n; w++) { 
        int i = pos[w];
        if (i == n - 1) {
            l = 0;
            continue;
        }
        int v = sufarr[i + 1];
        // std::cout << "checking " << w << " " << v << std::endl; 
        l = std::max(l - 1, 0);
        while (v + l < n && w + l < n && s[v + l] == s[w + l]) {
            l++;
        }
        // std::cout << "ans: " << l << std::endl;
        lcp[i] = l;
    } 
    return lcp;
}

std::string find_kth_unique_substring(const std::string& s, long long k) {
    auto sufarr = find_sufarr(s);
    auto lcp = find_lcp(s, sufarr);
    int n = s.length();
    lcp.insert(lcp.begin(), 0);
    // for (auto t : sufarr)
        // std::cout << t << " ";
    // std::cout << std::endl;
    // for (auto t : lcp)
        // std::cout << t << " ";
    // std::cout << std::endl;
    for (int i = 0; i < n; i++) {
        int count_substrings = (n - sufarr[i]) - lcp[i];
        // std::cout << count_substrings << std::endl; 
        if (k > count_substrings) {
            k -= count_substrings;
        } else {
            return s.substr(sufarr[i], lcp[i] + k);
        }
        if (i == n - 1) {
            return s.substr(sufarr[i], n - sufarr[i]);
        }
    }
    
}

main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(0);
    std::string s = "";
    long long k = 0;
    std::cin >> s >> k;
    std::cout << find_kth_unique_substring(s, k);
}
