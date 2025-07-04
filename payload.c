#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <windows.h>
#include <winternl.h>

int main(void) {
  WinExec("calc.exe", SW_SHOWNORMAL);
  VirtualAlloc(NULL, 100, NULL, NULL);
  return 0;
}
