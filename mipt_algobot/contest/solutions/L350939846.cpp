#include <iostream>
#include <vector>
#include <cstring>
#include <map>

struct node
        {
    int link;
    int len;
    int to[26];
    int cnt;
    int used = 0;
    node(int l = 0): link(-1), len(l), cnt(0), used(-1) {
        memset(to, -1, sizeof(to));
    };
        };

void add(std::vector<node>& t, int& last, int c)
{
    int cur = t.size();
    t.emplace_back(t[last].len + 1);
    t.back().cnt = 1;
    int p = last;
    while (p != -1 && t[p].to[c] == -1) {
        t[p].to[c] = cur;
        p = t[p].link;
    }
    if (p == -1) {
        t[cur].link = 0;
        last = t[last].to[c];
        return;
    }
    int q = t[p].to[c];
    if (t[q].len == t[p].len + 1) {
        t[cur].link = q;
        last = t[last].to[c];
        return;
    }
    int clone = t.size();
    t.emplace_back(t[p].len + 1);
    t[clone].link = t[q].link;
    t[q].link = t[cur].link = clone;
    for (int i = 0; i < 26; ++i)
        t[clone].to[i] = t[q].to[i];
    while (p != -1 && t[p].to[c] == q) {
        t[p].to[c] = clone;
        p = t[p].link;
    }
    last = t[last].to[c];
}

void update_cnt(std::vector<node>& t)
{
    std::multimap<int, int> m;
    for (int i = 0; i < t.size(); ++i)
        m.insert({t[i].len, i});
    for (auto it = m.rbegin(); it != m.rend(); ++it)
        if (t[it->second].link != -1)
            t[t[it->second].link].cnt += t[it->second].cnt;
}

int counter = 0;

int find_ans(std::vector<node>& t, const std::string& s)
{
    ++counter;
    int curr = 0;
    int len = 0;
    for (char i: s) {
        while (curr != -1 && t[curr].to[i - 'a'] == -1) {
            curr = t[curr].link;
            len = t[curr].len;
        }
        if (curr == -1)
            return 0;
        curr = t[curr].to[i - 'a'];
        ++len;
    }

    int ans = 0;
    for (int i = 0; i < s.size(); ++i) {
        while (t[curr].to[s[i] - 'a'] == -1) {
            curr = t[curr].link;
            len = t[curr].len;
        }
        curr = t[curr].to[s[i] - 'a'];
        ++len;

        while (len > s.size() && t[curr].link != -1 && t[t[curr].link].len >= s.size()) {
            curr = t[curr].link;
            len = t[curr].len;
        }

        if (len >= s.size() && t[curr].used < counter) {
            ans += t[curr].cnt;
            t[curr].used = counter;
        }

        int k = 0;
    }
    return ans;
}

int main()
{
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::cout.tie(nullptr);
    std::vector<node> t;
    t.emplace_back();
    int last = 0;
    std::string s;
    std::cin >> s;
    for (char c: s)
        add(t, last, c - 'a');
    update_cnt(t);
    int n;
    std::cin >> n;
    for (int i = 0; i < n; ++i) {
        std::string text;
        std::cin >> text;
        std::cout << find_ans(t, text) << '\n';
    }
}
