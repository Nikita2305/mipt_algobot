#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
#include <unordered_set>

std::vector<int> res;

struct node
        {
    node* parent;
    std::vector<node*> children;
    int height;
    int term;
    node(node* p, int h, int term = -1): parent(p), height(h), term(term) {};
    ~node() {
        for (auto* child: children)
            delete child;
    }
        };

node* add_suffix(node* cur, int length, int lcp, int term)
{
    if (cur->height == 0 || cur->height == lcp) {
        node* new_node = new node(cur, length, term);
        cur->children.push_back(new_node);
        return new_node;
    } else {
        if (cur->parent->height < lcp) {
            node* cut = new node(cur->parent, lcp);
            cur->parent->children.back() = cut;
            cut->children.push_back(cur);
            cur->parent = cut;
        }
        return add_suffix(cur->parent, length, lcp, term);
    }
}

node* build_tree(std::vector<int>& p, std::vector<int>& lcp, int size, std::map<int, int>& m)
{
    node* root = new node(nullptr, 0);
    node* new_node = new node(root, 1, 0);
    root->children.push_back(new_node);
    node* cur = new_node;
    for (int i = 0; i < size - 1; ++i) {
        auto it = m.lower_bound(p[i + 1]);
        cur = add_suffix(cur, it->first + 1 - p[i + 1], lcp[i], it->second);
    }
    return root;
}

std::unordered_set<int> dfs(node* root, int num)
{
    std::unordered_set<int> ans;
    if (root->term != -1) {
        ans.insert(root->term);
        return ans;
    }
    for (auto* child: root->children) {
        auto child_ans = dfs(child, num);
        for (auto& it: child_ans)
            ans.insert(it);
    }
    int count = ans.size();
    res[count] = std::max(root->height, res[count]);
    return ans;
}

int main()
{
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::cout.tie(nullptr);
    std::vector<int> s;
    int num;
    std::cin >> num;
    std::map<int, int> m;
    for (int i = 0; i < num; ++i) {
        std::string s1;
        std::cin >> s1;
        for (char c: s1)
            s.push_back(num + c - 97);
        m.insert({s.size(), i});
        s.push_back(i);
    }
    int size = static_cast<int>(s.size());
    std::vector<int> p(size), c(size);
    std::vector<int> cnt(num + 26, 0);
    for (int ch: s)
        ++cnt[ch];
    int sum = 0;
    for (int i = 0; i < num + 26; ++i) {
        int delta = cnt[i];
        cnt[i] = sum;
        sum += delta;
    }
    for (int i = 0; i < size; ++i)
        p[cnt[s[i]]++] = i;
    int count = 0;
    c[p[0]] = count;
    for (int i = 1; i < size; ++i) {
        if (s[p[i]] != s[p[i - 1]])
            ++count;
        c[p[i]] = count;
    }
    for (int k = 0; (1 << k) <= size; ++k) {
        std::vector<int> pn(size), cn(size);
        for (int i = 0; i < size; ++i) {
            pn[i] = (size + p[i] - (1 << k)) % size;
        }
        std::vector<int> cntn(count + 1, 0);
        for (int i = 0; i < size; ++i)
            ++cntn[c[pn[i]]];
        sum = 0;
        for (int i = 0; i <= count; ++i) {
            int delta = cntn[i];
            cntn[i] = sum;
            sum += delta;
        }
        for (int i = 0; i < size; ++i)
            p[cntn[c[pn[i]]]++] = pn[i];
        cn[p[0]] = 0;
        count = 0;
        for (int i = 1; i < size; ++i) {
            if (c[p[i]] != c[p[i - 1]] || c[(size + p[i] + (1 << k)) % size] != c[(size + p[i - 1] + (1 << k)) % size])
                ++count;
            cn[p[i]] = count;
        }
        c = cn;
    }
    std::vector<int> lcp(size - 1, 0);
    std::vector<int> p_inv(size);
    for (int i = 0; i < size; ++i)
        p_inv[p[i]] = i;
    int l = 0;
    for (int w = 0; w < size - 1; ++w) {
        int i = p_inv[w];
        if (i == size - 1) {
            l = 0;
            continue;
        }
        int j = p[i + 1];
        l = std::max(l - 1, 0);
        while (w + l < size && j + l < size && s[w + l] == s[j + l])
            ++l;
        lcp[i] = l;
    }
    node* root = build_tree(p, lcp, size, m);
    res.assign(num + 1, 0);
    dfs(root, num);
    int curr_max = -1;
    for (int i = num; i >= 2; --i)
        res[i] = curr_max = std::max(curr_max, res[i]);
    for (int i = 2; i <= num; ++i)
        std::cout << res[i] << '\n';
    delete root;
}
