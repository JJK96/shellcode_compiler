#![no_main]
use windows_sys::{
    core::*, Win32::System::Threading::*, Win32::UI::WindowsAndMessaging::*,
};

extern "C" {
    fn printf(format: *const u8, ...) -> i32;
}

#[no_mangle]
fn main() -> () {
    unsafe {
        WinExec(s!("calc.exe"), SW_SHOWNORMAL.try_into().unwrap());
        printf(s!("Test\n"));
    }
}
