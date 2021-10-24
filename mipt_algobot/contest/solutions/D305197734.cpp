#include <iostream>
#include <vector>

class Tree {
public:
    Tree(const std::vector<int>& v) {
        tree.resize(4 * v.size() + 10);
        build(1, 0, v.size() - 1, v);
    } 
    std::pair<int, int> get(int v, int tl, int tr, int l, int r) {
        if (l > r) {
            return getE();
        }
        if (tl == l && tr == r) {
            return tree[v];
        }
        int tm = (tl + tr) / 2;
        return combine(get(v * 2, tl, tm, l, std::min(r, tm)), get(v * 2 + 1, tm + 1, tr, std::max(tm + 1, l), r));
    }
private:
    std::vector<std::pair<int, int>> tree;
    void build(int v, int tl, int tr, const std::vector<int>& arr) {
        if (tl == tr) {
            tree[v] = {arr[tl], arr[tl]};
            return;
        }
        int tm = (tl + tr) / 2;
        build(v * 2, tl, tm, arr);
        build(v * 2 + 1, tm + 1, tr, arr);  
        tree[v] = combine(tree[v * 2], tree[v * 2 + 1]);
    }
    std::pair<int, int> combine(std::pair<int, int> a, std::pair<int, int> b) {
        return {std::min(a.first, b.first), std::max(a.second, b.second)};
    }
    std::pair<int, int> getE() {
        return {1e9, -1e9};
    }
};

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
    for (int i = 1; i < count.size(); i++) {
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
        l = std::max(l - 1, 0);
        while (v + l < n && w + l < n && s[v + l] == s[w + l]) {
            l++;
        }
        lcp[i] = l;
    } 
    return lcp;
}

long long solve(const std::string& s) {
    if (s.length() == 1) {
        return 1;
    }
    auto sufarr = find_sufarr(s);
    auto lcp = find_lcp(s, sufarr);
    int n = s.length();
    /*for (auto t : sufarr) {
        std::cout << t << " ";
    }
    std::cout << std::endl;
    for (auto t : lcp) {
        std::cout << t << " ";
    }
    std::cout << std::endl;
    */std::vector<int> left(n), right(n);
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
    /*
    for (int i = 0; i < lcp.size(); i++) {
        std::cout << "{" << left[i] << "," << right[i] << "} ";
    }
    std::cout << std::endl;*/
    Tree tree(sufarr);
    long long ans = 0;
    for (int i = 0; i < lcp.size(); i++) {
        int l = left[i] + 1;
        int r = right[i];
        // std::cout << l << " " << r << ": ";
        auto minmax = tree.get(1, 0, sufarr.size() - 1, l, r);
        long long attempt = (minmax.second - minmax.first) + lcp[i] + 1ll * lcp[i] * lcp[i];
        // std::cout << minmax.first << " " << minmax.second << " " << attempt << std::endl;
        ans = std::max(ans, (minmax.second - minmax.first) + std::max(lcp[i], 1) + 1ll * lcp[i] * lcp[i]);
    }
    return ans;
}

main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(0);
    std::string s;
    std::cin >> s;
    std::cout << solve(s);
}
