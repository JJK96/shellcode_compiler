#![no_main]
use windows_sys::{
    core::*, Win32::System::Threading::*, Win32::UI::WindowsAndMessaging::*,
};
use libc::*;

#[no_mangle]
fn main() -> () {
    unsafe {
        WinExec(s!("calc.exe"), SW_SHOWNORMAL.try_into().unwrap());
        printf(s!("Test\n") as *const i8);
    }
}
