fn main() {
    println!("{{\"program\":\"rust-bin\",\"os\":\"{}\",\"arch\":\"{}\",\"exe\":\"{}\"}}", std::env::consts::OS, std::env::consts::ARCH, std::env::current_exe().unwrap().display());
}
