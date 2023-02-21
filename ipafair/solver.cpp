#include <vector>
#include <set>
#include <map>
#include <array>
#include <string>
#include <algorithm>
#include <iostream>
#include <fstream>
#include <cstdio>

#ifndef EXTERNAL_AF_SOLVER
#define EXTERNAL_AF_SOLVER "./mu-toksia"
#endif

using namespace std;

class NaiveSolver {

public:
    NaiveSolver() : state(0) {}

    void set_semantics (uint8_t sem) {
        switch (sem) {
            case 1:
                semantics = "CO";
                break;
            case 2:
                semantics = "PR";
                break;
            case 3:
                semantics = "ST";
                break;
            case 4:
                semantics = "SST";
                break;
            case 5:
                semantics = "STG";
                break;
            case 6:
                semantics = "ID";
                break;
            default:
                state = -1;
                return;
        }
        state = 0;
    }

    void add_argument(int32_t argument) {
        if (argument <= 0 || arguments.count(argument)) {
            state = -1;
            return;
        }
        arguments.insert(argument);
        state = 0;
    }

    void del_argument(int32_t argument) {
        if (!arguments.count(argument)) {
            state = -1;
            return;
        }
        arguments.erase(argument);
        state = 0;
    }

    void add_attack(int32_t source, int32_t target) {
        if (!arguments.count(source) || !arguments.count(target)
            || attacks.count(make_pair(source,target))) {
            state = -1;
            return;
        }
        attacks.insert(make_pair(source, target));
        state = 0;
    }

    void del_attack(int32_t source, int32_t target) {
        if (!attacks.count(make_pair(source, target))) {
            state = -1;
            return;
        }
        attacks.erase(make_pair(source, target));
        state = 0;
    }

    void assume(int32_t argument) {
        if (!arguments.count(argument) || assumptions.size()) {
            state = -1;
            return;
        }
        assumptions.insert(argument);
    }

    int32_t solve(bool credulous_mode) {
        if (state < 0) return -1;
        if (semantics.empty()) return -1;
        if (assumptions.empty()) return -1;

        // create temporary apx file with current af
        string name = std::getenv("TMPDIR") + string("af.apx");
        ofstream file;
        file.open(name);
        for (int32_t argument : arguments) {
            file << "arg(" << argument << ").\n";
        }
        for (pair<int32_t,int32_t> attack : attacks) {
            file << "att(" << attack.first << "," << attack.second << ").\n";
        }
        file.close();

        // call external solver on the corresponding task
        string task = credulous_mode ? "DC-" + semantics : "DS-" + semantics;
        string query = to_string(*assumptions.begin());
        assumptions.clear();
        string command = EXTERNAL_AF_SOLVER + string(" -p ") + task
                         + string(" -f ") + name + string(" -fo apx -a ") + query;
        FILE * pipe = popen(command.c_str(), "r");
        if (!pipe) return -1;
        array<char, 128> buffer;
        string result;
        while (fgets(buffer.data(), 128, pipe) != NULL) {
            result += buffer.data();
        }
        pclose(pipe);
        remove(name.c_str());

        // parse the output
        result.erase(std::remove_if(result.begin(), result.end(), ::isspace), result.end());
        if (result == "YES") {
            return 10;
        } else if (result == "NO") {
            return 20;
        }
        return -1;
    }

    int32_t val(int32_t argument) {
        return 0; // redundant: no certificate needed for dynamic track
    }

private:
    int32_t state;
    string semantics;
    set<int32_t> arguments;
    set<pair<int32_t,int32_t>> attacks;
    set<int32_t> assumptions;

};

extern "C" {

#include "ipafair.h"

static NaiveSolver * import (void * s) { return (NaiveSolver *) s; }
const char * ipafair_signature () { return "ICCMA'23"; }
void * ipafair_init () { return new NaiveSolver(); }
void ipafair_release (void * s) { delete import(s); }
void ipafair_set_semantics (void * s, semantics sem) { import(s)->set_semantics(sem); }
void ipafair_add_argument (void * s, int32_t a) { import(s)->add_argument(a); }
void ipafair_del_argument (void * s, int32_t a) { import(s)->del_argument(a); }
void ipafair_add_attack (void * s, int32_t a, int32_t b) { import(s)->add_attack(a,b); }
void ipafair_del_attack (void * s, int32_t a, int32_t b) { import(s)->del_attack(a,b); }
void ipafair_assume (void * s, int32_t a) { import(s)->assume(a); }
int32_t ipafair_solve_cred (void * s) { return import(s)->solve(true); }
int32_t ipafair_solve_skept (void * s) { return import(s)->solve(false); }
int32_t ipafair_val (void * s, int32_t a) { return import(s)->val(a); }

};
