#include <iostream>
#include <vector>

std::vector<int> find_sufarr(std::string s) {
    s += "#";
    int n = s.length();   
    s += s;
    // let assume c[i] = class of i-th string in sort
    // thus c'[i] is obtained from {c[i], c[i + 2^k]}
    std::vector<int> c(n, -1), pos(n, 0);
    std::vector<int> count(10, 0);
    std::vector<int> v(n);
    for (int i = 0; i < n - 1; i++) {
        count[s[i] - '0'] = 1;
    }
    for (int i = 1; i < count.size(); i++) {
        count[i] += count[i - 1];
    }
    for (int i = 0; i < n - 1; i++) {
        c[i] = count[s[i] - '0'];
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
        l = std::max(l - 1, 0);
        while (v + l < n && w + l < n && s[v + l] == s[w + l]) {
            l++;
        }
        lcp[i] = l;
    } 
    return lcp;
}

std::pair<std::string, int> find_refren(const std::string& s) {
    auto sufarr = find_sufarr(s);
    auto lcp = find_lcp(s, sufarr);
    int n = s.length();
    int frequency = 1;
    int index = 0;
    int len = s.length();
    for (auto t : sufarr) {
        //std::cout << t << " ";
    }
    //std::cout << std::endl;
    for (auto t : lcp) {
        //std::cout << t << " ";
    }
    //std::cout << std::endl;
    std::vector<int> left(n), right(n);
    std::vector<int> st;
    for (int i = 0; i < lcp.size(); i++) {
        while (!st.empty() && lcp[st.back()] > lcp[i]) {
            right[st.back()] = i;
            st.pop_back();
        }
        st.push_back(i);
    }
    while (!st.empty()) {
        right[st.back()] = lcp.size();
        st.pop_back();
    }
    for (int i = (int)lcp.size() - 1; i >= 0; i--) {
        while (!st.empty() && lcp[st.back()] > lcp[i]) {
            left[st.back()] = i;
            st.pop_back();
        }
        st.push_back(i);
    }
    while (!st.empty()) {
        left[st.back()] = -1;
        st.pop_back();
    }
    for (int i = 0; i < lcp.size(); i++) {
        //std::cout << "{" << left[i] << "," << right[i] << "} ";
    }
    //std::cout << std::endl;
    for (int i = 0; i < lcp.size(); i++) {
        int size = right[i] - left[i];
        //std::cout << sufarr[i] << " " << lcp[i] << " " << size << std::endl;
        if (1ll * size * lcp[i] > 1ll * frequency * len) {
            index = sufarr[i];
            len = lcp[i];
            frequency = size;
        }
    }
    return {s.substr(index, len), frequency};
}

main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(0);
    int n = 0, k = 0;
    std::cin >> n >> k;
    std::string s(n, '0');
    for (int i = 0; i < n; i++) {
        int q = 0;
        std::cin >> q;
        s[i] += q - 1;
    }
    auto refren = find_refren(s);
    std::cout << 1ll * refren.second * refren.first.length() << std::endl;
    std::cout << refren.first.size() << std::endl;
    for (int i = 0; i < refren.first.size(); i++) {
        std::cout << 1 + (refren.first[i] - '0') << " ";
    }
    
}
