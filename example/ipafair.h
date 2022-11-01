/* This file is part of IPAFAIR, an incremental API for AF solvers.
 * 
 * This C version of IPAFAIR is based on the incremental SAT API IPASIR:
 * https://github.com/biotomas/ipasir
 * 
 * See LICENSE.md for rights to use this software.
 */
#ifndef ipafair_h_INCLUDED
#define ipafair_h_INCLUDED

#include <stdint.h>

/*
 * In this header, the macro IPAFAIR_API is defined as follows:
 * - if IPAFAIR_SHARED_LIB is not defined, then IPAFAIR_API is defined, but empty.
 * - if IPAFAIR_SHARED_LIB is defined...
 *    - ...and if BUILDING_IPAFAIR_SHARED_LIB is not defined, IPAFAIR_API is
 *      defined to contain symbol visibility attributes for importing symbols
 *      of a DSO (including the __declspec rsp. __attribute__ keywords).
 *    - ...and if BUILDING_IPAFAIR_SHARED_LIB is defined, IPAFAIR_API is defined
 *      to contain symbol visibility attributes for exporting symbols from a
 *      DSO (including the __declspec rsp. __attribute__ keywords).
 */

#if defined(IPAFAIR_SHARED_LIB)
    #if defined(_WIN32) || defined(__CYGWIN__)
        #if defined(BUILDING_IPAFAIR_SHARED_LIB)
            #if defined(__GNUC__)
                #define IPAFAIR_API __attribute__((dllexport))
            #elif defined(_MSC_VER)
                #define IPAFAIR_API __declspec(dllexport)
            #endif
        #else
            #if defined(__GNUC__)
                #define IPAFAIR_API __attribute__((dllimport))
            #elif defined(_MSC_VER)
                #define IPAFAIR_API __declspec(dllimport)
            #endif
        #endif
    #elif defined(__GNUC__)
        #define IPAFAIR_API __attribute__((visibility("default")))
    #endif

    #if !defined(IPAFAIR_API)
        #if !defined(IPAFAIR_SUPPRESS_WARNINGS)
            #warning "Unknown compiler. Not adding visibility information to IPAFAIR symbols."
            #warning "Define IPAFAIR_SUPPRESS_WARNINGS to suppress this warning."
        #endif
        #define IPAFAIR_API
    #endif
#else
    #define IPAFAIR_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    admissible,
    complete,
    preferred,
    stable,
    semistable,
    stage,
    ideal
} semantics;

/**
 * Return the name and the version of the dynamic AF solver.
 */
IPAFAIR_API const char * ipafair_signature ();

/**
 * Construct a new solver and return a pointer to it. Use the returned pointer
 * as the first parameter in each of the following functions.
 *
 * Required state: N/A
 * State after: INPUT
 */
IPAFAIR_API void * ipafair_init ();

/**
 * Release the solver, i.e., all its resources and allocated memory. The solver
 * pointer cannot be used for any purposes after this call.
 *
 * Required state: INPUT or SAT or UNSAT or ERROR
 * State after: undefined
 */
IPAFAIR_API void ipafair_release (void * solver);

/**
 * Set the argumentation semantics for the next calls of 'ipafair_solve'.
 * 
 * If the semantics is not supported by the solver, enter state ERROR.
 * 
 * Required state: INPUT or SAT or UNSAT
 * State after: INPUT or ERROR
 */
IPAFAIR_API void ipafair_set_semantics (void * solver, semantics sem);

/**
 * Add the given argument to the current argumentation framework.
 * 
 * If the argument already exists, enter state ERROR.
 * 
 * Arguments are encoded as positive integers. They have to be smaller or equal
 * to INT32_MAX. This applies to all the literal arguments in API functions.
 * 
 * Required state: INPUT or SAT or UNSAT
 * State after: INPUT or ERROR
 */
IPAFAIR_API void ipafair_add_argument (void * solver, int32_t arg);

/**
 * Delete the given argument from the current argumentation framework.
 *
 * If the argument does not exist, enter state ERROR.
 * 
 * Required state: INPUT or SAT or UNSAT
 * State after: INPUT or ERROR
 */
IPAFAIR_API void ipafair_del_argument (void * solver, int32_t arg);

/**
 * Add the given attack (s,t) to the current argumentation framework.
 * 
 * If the attack already exists, or if s or t is not an existing argument
 * added via 'ipafair_add_argument', enter state ERROR.
 * 
 * Required state: INPUT or SAT or UNSAT
 * State after: INPUT or ERROR
 */
IPAFAIR_API void ipafair_add_attack (void * solver, int32_t s, int32_t t);

/**
 * Delete the given attack (s,t) from the current argumentation framework.
 * 
 * If the attack does not exist, enter state ERROR.
 * 
 * Required state: INPUT or SAT or UNSAT
 * State after: INPUT or ERROR
 */
IPAFAIR_API void ipafair_del_attack (void * solver, int32_t s, int32_t t);

/**
 * Add an assumption for the next call of 'ipafair_solve'. After calling
 * 'ipafair_solve' all previously added assumptions are cleared.
 * 
 * The assumption is provided as a positive integer whose value is an argument
 * previously added via 'ipafair_add_argument'.
 * 
 * If such an argument does not exist, enter state ERROR.
 * 
 * Required state: INPUT or SAT or UNSAT
 * State after: INPUT or ERROR
 */
IPAFAIR_API void ipafair_assume (void * solver, int32_t arg);

/**
 * Solve the current instance, as defined by previous calls to
 * 'ipafair_set_semantics', 'ipafair_add_argument', 'ipafair_del_argument',
 * 'ipafair_add_attack', 'ipafair_del_attack', and 'ipafair_assume'
 * in the credulous reasoning mode.
 * 
 * That is, decide whether arguments assumed via 'ipafair_assume' are contained
 * in *an extension* under semantics specified by 'ipafair_set_semantics' in
 * the current argumentation framework constructed by calls to
 * 'ipafair_add_argument', 'ipafair_del_argument', 'ipafair_add_attack', and
 * 'ipafair_del_attack'.
 * 
 * If the answer is 'yes', return 10 and change the state of the solver to SAT.
 * If the answer is 'no', return 20 and change the state of the solver to UNSAT.
 * If the solver does not support the sequence of API calls performed, return -1
 * and change the state of the solver to ERROR.
 * 
 * This function can be called in any defined state of the solver. Note that
 * the state of the solver _during_ execution of 'ipafair_solve' is undefined.
 *
 * Required state: INPUT or SAT or UNSAT
 * State after: SAT or UNSAT or ERROR
 */
IPAFAIR_API int ipafair_solve_cred (void * solver);

/**
 * Solve the current instance, as defined by previous calls to
 * 'ipafair_set_semantics', 'ipafair_add_argument', 'ipafair_del_argument',
 * 'ipafair_add_attack', 'ipafair_del_attack', and 'ipafair_assume'
 * in the skeptical reasoning mode.
 * 
 * That is, decide whether arguments assumed via 'ipafair_assume' are contained
 * in *all extensions* under semantics specified by 'ipafair_set_semantics' in
 * the current argumentation framework constructed by calls to
 * 'ipafair_add_argument', 'ipafair_del_argument', 'ipafair_add_attack', and
 * 'ipafair_del_attack'.
 * 
 * If the answer is 'yes', return 10 and change the state of the solver to SAT.
 * If the answer is 'no', return 20 and change the state of the solver to UNSAT.
 * If the solver does not support the sequence of API calls performed, return -1
 * and change the state of the solver to ERROR.
 * 
 * This function can be called in any defined state of the solver. Note that
 * the state of the solver _during_ execution of 'ipafair_solve' is undefined.
 *
 * Required state: INPUT or SAT or UNSAT
 * State after: SAT or UNSAT or ERROR
 */
IPAFAIR_API int ipafair_solve_skept (void * solver);

/**
 * Determine whether the given argument is contained in a solution or
 * counterexample extension. Return 'arg' if the answer is 'yes', and '-arg'
 * if the answer is 'no'.
 * 
 * This function can only be used if 'ipafair_solve_cred' has returned 10, or
 * 'ipafair_solve_skept' has returned 20, and the state of the solver has not
 * changed.
 * 
 * Required state: SAT or UNSAT
 * State after: SAT or UNSAT (unchanged)
 */
IPAFAIR_API int32_t ipafair_val (void * solver, int32_t arg);

#ifdef __cplusplus
} // closing extern "C"
#endif

#endif
