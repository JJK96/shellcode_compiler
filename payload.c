#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <windows.h>
#include <winternl.h>

// __attribute__ ((noinline)) __attribute__((section(".end"))) int end(void) { }

int start(void) {
  WinExec("calc.exe", SW_SHOWNORMAL);
  return 0;
  // return end();
}
