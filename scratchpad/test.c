#include "../lib_boa/boa_runtime.h"
#include <stdio.h>
#include <stdlib.h>

int main(int a, int b) {
  float x0;
  float x1;
  x0 = 10000;

  for (x1 = 1; x1 < x0; x1 += 1) {
    boa_print(bNumber(x0));
  }

  return 0;
}
