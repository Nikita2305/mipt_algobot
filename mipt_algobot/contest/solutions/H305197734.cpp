#include <iostream>
#include <vector>

char nullchar = 'a' - 1;

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
    std::vector<int> count(27, 0);
    std::vector<int> v(n);
    for (int i = 0; i < n - 1; i++) {
        count[s[i] - nullchar] = 1;
    }
    for (int i = 1; i < count.size(); i++) {
        count[i] += count[i - 1];
    }
    for (int i = 0; i < n - 1; i++) {
        c[i] = count[s[i] - nullchar];
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

bool is_full(const std::vector<int>& v) {
    for (auto t : v) {
        if (t == 0) {
            return false;
        }
    }
    return true;
}

std::string find_max_common_substring(const std::vector<std::string>& v) {
    if (v.size() == 1) {
        return v[0];
    }
    std::string s = "";
    std::vector<int> limits;
    int length = 0;
    for (auto& t : v) {
        s += t;
        s += nullchar;
        length += t.length() + 1;
        limits.push_back(length - 1);
    }
    s.pop_back();
    //std::cout << s << std::endl;
    auto sufarr = find_sufarr(s);
    auto lcp = find_lcp(s, sufarr);
    int n = s.length();
    //std::cout << sufarr[0];
    for (int i = 1; i < n; i++) {
        //std::cout << " (" << lcp[i - 1] << ") " << sufarr[i];
    }
    //std::cout << std::endl;
    std::vector<int> availability(v.size());
    Tree tree(lcp);
    int ptr = v.size() - 1; 
    int len_ans = -1;
    int index_ans = -1;
    for (int i = v.size() - 1; i < n; i++) { // start from v.size() to pass the nullchars
        while (ptr < n && !is_full(availability)) { 
            int index = lower_bound(limits.begin(), limits.end(), sufarr[ptr]) - limits.begin();  
            //std::cout << "add " << sufarr[ptr] << " index: " << index << std::endl;
            availability[index]++;
            ptr++;
        }
        if (is_full(availability)) {
            //std::cout << "count min from " << i << " to " << ptr - 2 << std::endl;
            auto minmax = tree.get(1, 0, lcp.size() - 1, i, ptr - 2);
            //std::cout << "ans is " << minmax.first << std::endl;
            if (minmax.first > len_ans) {
                index_ans = sufarr[i];
                len_ans = minmax.first;
            }
        }
        int index = lower_bound(limits.begin(), limits.end(), sufarr[i]) - limits.begin();  
        availability[index]--;
        //std::cout << "erase " << sufarr[i] << " index: " << index << std::endl << std::endl;
    }
    return s.substr(index_ans, len_ans);
}

main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(0);
    int n = 0;
    std::cin >> n;
    std::vector<std::string> v(n);
    for (auto& t : v) {
        std::cin >> t;
    }
    std::cout << find_max_common_substring(v);
}
