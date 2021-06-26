#ifndef BOA_RUNTIME_H
#define BOA_RUNTIME_H

#include <stdbool.h>
#include <stdio.h>

typedef float boaNumber;

typedef enum {
    V_NUM,
    V_STR,
    V_BOOL,
    V_OBJ
} BVKind;

typedef struct {
    BVKind tag;
    union {
        boaNumber numVal;
        void* objVal;
        bool boolVal;
    } as;
} BoaValue;


#define BOA_AS_NUM(v) (v.as.numVal)
#define BOA_IS_NUM(v) (v.tag == V_NUM)

BoaValue bNumber(boaNumber value) {
    BoaValue v;
    v.as.numVal = value;
    v.tag = V_NUM;
    return v;
}

void boa_print(BoaValue v) {
    printf("%f\n", v.as.numVal);
}


#endif