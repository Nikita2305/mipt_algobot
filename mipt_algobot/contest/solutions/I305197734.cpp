#include <iostream>
#include <vector>
#include <map>
#include <tuple>

struct Node { // Could be edge-vertex
    Node(int l, int r, Node* par): l(l), r(r), par(par) {
        ////std::cout << "Creating Node(" << l << "," << r << ")" << std::endl;
    }
    std::map<char, Node*> edges;
    int l = 0; // Means that we are here by s[l..r] edge
    int r = 0; 
    Node* par = nullptr;
    Node* link = nullptr;
};

// State, which is Node: {par, c, len} but not {node, 'a', 0}
struct State {
    Node* node;
    char c;
    int len;
    bool operator==(const State& s) {
        return node == s.node && c == s.c && len == s.len;
    }
    bool operator!=(const State& s) {
        return !(*this == s);
    }
};

class SufTree {
public:
    SufTree(const std::string& s): S(s) {
        root = new Node(-1, -1, nullptr); 
        root_state = {root, ')', -1};
        State state = root_state;
        for (int i = 0; i < s.length(); i++) {
            char c = s[i];
            //std::cout << "---- Add char " << c << " ----" << std::endl; 
            Node* to_set_link = nullptr;
            while (true) {
                //std::cout << "State: " << state.node->l << " " << state.node->r << " " << state.c << " " << state.len << std::endl;
                // Проверяем, есть ли из данного стейта путь по букве с
                    // если нет, то создаём ветвление 
                    // + выполняем обещание, если есть и если можем
                    // + создаём обещание, если ответвились
                bool isNode = false;
                if (state == root_state) {
                    isNode = true;
                } else {
                    Node* dest_node = state.node->edges[state.c];
                    isNode = (dest_node->l + state.len - 1 == dest_node->r); 
                }
                if (isNode) { // Случай, что стейт = вершина (dest_node)
                    //std::cout << "State is node" << std::endl;
                    Node* dest_node = root;
                    if (state != root_state) {
                        dest_node = state.node->edges[state.c];
                    }
                    if (to_set_link) {
                        to_set_link->link = dest_node;
                        to_set_link = nullptr;
                    }
                    if (dest_node->edges.find(c) != dest_node->edges.end()) {
                        //std::cout << "Found such symbol" << std::endl;
                        state = State{dest_node, c, 1};
                        break;
                    } else { // Если такого символа нет - то создаём ветку до конца.
                        //std::cout << "No such symbol, creaing line" << std::endl;
                        dest_node->edges[c] = new Node(i, s.length() - 1, dest_node);
                    }
                } else { // Cлучай, когда стейт на ребре.
                    //std::cout << "State is on edge" << std::endl;
                    Node* dest_node = state.node->edges[state.c];
                    // //////std::cout << "Dest_node " << dest_node->l << " " << dest_node->r << std::endl;
                    char x = s[dest_node->l + state.len]; // Следующий символ после нашего стейта
                    // //////std::cout << "Next symb is " << x << std::endl;
                    if (x == c) {
                        //std::cout << "Found such symbol" << std::endl; 
                        state = State{state.node, state.c, state.len + 1};
                        // мы в ситуации, когда никакой вершины не добавилось. Утверждается, что тогда и не было обещания
                        break;
                    } else { // Если не тот символ след., то создаём ветвление
                        //std::cout << "No such symbol, inserting on edge..." << std::endl;
                        Node* inserted = new Node(dest_node->l, dest_node->l + state.len - 1, state.node);
                        state.node->edges[state.c] = inserted;
                        dest_node->l = dest_node->l + state.len;
                        ////std::cout << "old node changed " << dest_node->l << " " << dest_node->r << std::endl;
                        dest_node->par = inserted;
                        inserted->edges[x] = dest_node;
                        inserted->edges[c] = new Node(i, s.length() - 1, inserted); 
                        if (to_set_link) {
                            to_set_link->link = inserted; 
                        }
                        to_set_link = inserted; // Если пришлось сплитнуть ребро, то добавляем обещание.
                    }
                }
                //std::cout << "Work is over" << std::endl; 
                // Если вдруг мы уже исчерапали все суффиксы
                if (state == root_state) {
                    if (to_set_link) {
                        to_set_link->link = root;
                    }
                    break;
                } 
                //std::cout << "Changing state" << std::endl;
                // Переходим к суффиксу на 1 поменьше.
                state = getLink(state);
                //std::cout << "State changed" << std::endl;
            }
        }
    }
    std::vector<std::tuple<int,int,int>> getStructure() {
        ans.clear();
        ptr = 0;
        dfs(root, -1);
        return ans;
    } 
private:
    Node* root;
    const std::string& S;
    State root_state;
    std::vector<std::tuple<int,int,int>> ans;
    int ptr = 0;
    State getLink(State state) { // state != root_state. If State is Node => counts from Node->par
        Node* node = state.node; 
        if (node == root && state.len == 1) {
            return root_state;
        }
        Node* dest_node = state.node->edges[state.c];
        int l, r;
        if (node == root) {
            l = dest_node->l + 1, r = dest_node->l + state.len - 1;
        } else {
            l = dest_node->l, r = dest_node->l + state.len - 1;
            node = node->link;
        }
        //std::cout << "getLink: " << std::endl;
        //std::cout << "node: " << node->l << " " << node->r << std::endl;
        //std::cout << "s: " << l << " " << r << std::endl;
        // l <= r
        while (true) {
            //std::cout << "Jumping by char " << S[l] << std::endl;
            Node* dest_node = node->edges[S[l]]; // nullptr
            if (r - l <= dest_node->r - dest_node->l) {
                break;
            } else { // r - l > dest_node->r - dest_node->l
                l += dest_node->r - dest_node->l + 1;
                node = dest_node;
            }
        }
        return State{node, S[l], r - l + 1};
    }
    void dfs(Node* node, int par_id) {
        int my_id = ptr++;
        if (node != root) {
            ans.push_back(std::make_tuple(par_id, node->l, node->r + 1));
        }
        for (auto t : node->edges) {
            dfs(t.second, my_id);
        }
    }
};

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(0); 
    std::string s = "";
    std::cin >> s;
    SufTree tree(s);
    auto v = tree.getStructure();
    std::cout << v.size() + 1 << std::endl;
    for (auto t : v) {
        int a, b, c;
        std::tie(a, b, c) = t;
        std::cout << a << " " << b << " " << c << "\n";
    }
}
