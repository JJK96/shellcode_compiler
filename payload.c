#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <windows.h>
#include <winternl.h>

#define ENTRY __attribute__((section(".crtentry")))

ENTRY int start(void) {
  WinExec("calc.exe", SW_SHOWNORMAL);
  return 0;
}
