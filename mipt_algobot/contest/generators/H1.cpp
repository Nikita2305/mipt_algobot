/*#include <iostream>
#include <vector>

using namespace std;

//#define int long long

const int alph = 26;

vector<vector<unsigned int>> dp;

struct vertex {
    int link;
    int len;
    vector<int> to;
    int term;

    vertex() {
        link = -1;
        len = -1;
        to.assign(alph, -1);
        term = 0;
    }
};


class suf_auto {
public:
    suf_auto(int K) {
        lasts.resize(K, 0);
        t.push_back(vertex());
        t[0].len = 0;
        sz = 1;
    }

    void add(int num, char c) {
        int last = lasts[num];
        int curr = 0;
        int p = last;
        if (t[last].to[c - 'a'] != -1){
            if (t[t[last].to[c - 'a']].len == t[last].len + 1) {

            } else {

            }
            lasts[num] = t[last].to[c - 'a'];
            return;
        } else {
            sz += 1;
            t.push_back(vertex());
            curr = t.size() - 1;
            t[curr].len = t[last].len + 1;
        }
        while(p != -1 && t[p].to[c - 'a'] == -1) {
            t[p].to[c - 'a'] = curr;
            p = t[p].link;
        }
        if (p == -1) {
            t[curr].link = 0;
            lasts[num] = curr;
            return;
        }
        int q = t[p].to[c - 'a'];
        if (t[q].len == t[p].len + 1) {
            t[curr].link =  q;
            lasts[num] = curr;
            return;
        }
        sz += 1;
        t.push_back(vertex());
        int clone = t.size() - 1;
        t[clone].len = t[p].len + 1;
        while(p != -1 && t[p].to[c - 'a'] == q) {
            t[p].to[c - 'a'] = clone;
            p = t[p].link;
        }
        t[clone].to = t[q].to;
        t[clone].link = t[q].link;
        t[q].link = clone;
        t[curr].link = clone;
        lasts[num] = curr;
    }


    void count_term() {
        for (int i = 0; i < lasts.size(); ++i) {
            int a = i / 32;
            int b = i % 32;
            unsigned int res = 1 << b;
            int v = lasts[i];
            while(v != -1) {
                dp[v][a] |= res;
                v = t[v].link;
            }
        }

    }

    std::vector<int> obhod(int v) {
        std::vector<int> o;
        std::vector<bool> used(sz, 0);
        dfs(0, o, used);
        return o;
    }

    int get_to(int v, int c) {
        return t[v].to[c];
    }

    int get_size() {
        return t.size();
    }

    int get_len(int v) {
        return t[v].len;
    }

private:
    vector<vertex> t;
    vector<int> lasts;
    int sz;

    void dfs(int v, vector<int>& o, vector<bool>& used) {
        used[v] = 1;
        for (int i = 0; i < alph; ++i) {
            if (t[v].to[i] != -1 && used[t[v].to[i]] == 0) {
                dfs(t[v].to[i], o, used);
            }
        }
        o.push_back(v);
    }
};

signed main() {
    int N = 0;
    cin >> N;
    suf_auto at(N);
    int sz = N / 32 + 1;
    for (int i = 0; i < N; ++i) {
        string str;
        cin >> str;
        for (auto& c : str) {
            at.add(i, c);
        }
    }
    dp.resize(at.get_size(), vector<unsigned int> (sz, 0));
    at.count_term();
    auto o = at.obhod(0);
    vector<int> ans(N + 1, 0);
    for (int i = 0; i < o.size(); ++i) {
        for (int c = 0; c < alph; ++c) {
            int v = at.get_to(o[i], c);
            if (v == -1) continue;
            for (int t = 0; t < sz; ++t) {
                dp[o[i]][t] |= dp[v][t];
            }
            int a = 0;
            for (int t = 0 ; t < sz; ++t) {
                unsigned int temp = dp[o[i]][t];
                while(temp > 0) {
                    a += temp % 2;
                    temp >>= 1;
                }
            }
            ans[a] = max(ans[a], at.get_len(o[i]));
        }
    }
    int m = 0;
    for (int i = N; i >= 0; --i) {
        m = max(m, ans[i]);
        ans[i] = m;
    }
    for (int i = 2; i <= N; ++i) {
        cout << ans[i] << '\n';
    }
    return 0;
}*/

#include <iostream>
#include <time.h>
int lb, ub;
int alph;
std::string str;

void gen_str() {
    int lenght = lb + (rand() % (ub - lb + 1));
    str.clear();
    for (int i = 0; i < lenght; ++i) {
        str.push_back((char)('a' + (rand() % alph)));
    }
    std::cout << str << '\n';
}

int main() {
    clock();
    srand(10 * time(0) + clock()); // To make it more randomized
    str.reserve(20);
    int K = 1 + rand() % 10;
    alph = 1 + rand() % 26;
    std::cout << K << '\n';
    lb = 1 + rand() % 10;
    ub = lb + rand() % 10;
    for (int i = 0; i < K; ++i) {
        gen_str();
    }
}
