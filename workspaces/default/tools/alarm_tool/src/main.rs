use serde_json::Value;
use std::io;

fn main() {
    let mut input = String::new();
    if io::stdin().read_line(&mut input).is_ok() {
        if let Ok(parsed) = serde_json::from_str::<Value>(&input) {
            let args = parsed["args"].as_str().unwrap_or("");
            let response = serde_json::json!({
                "status": "set",
                "message": args
            });
            println!("{}", response);
        }
    }
}