use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct User {
    id: u64,
    name: String,
    email: String,
    #[serde(default)]
    is_active: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    bio: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
enum ApiResponse {
    Success { data: Vec<User> },
    Error { code: u16, message: String },
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Serialize to JSON
    let user = User {
        id: 1,
        name: "Alice".into(),
        email: "alice@example.com".into(),
        is_active: true,
        bio: None,
    };
    let json = serde_json::to_string_pretty(&user)?;
    println!("Serialized:\n{}", json);

    // Deserialize from JSON
    let input = r#"{"id":2,"name":"Bob","email":"bob@example.com"}"#;
    let user: User = serde_json::from_str(input)?;
    assert_eq!(user.name, "Bob");
    assert!(!user.is_active); // default applied

    // Tagged enum deserialization
    let success_response = r#"{"type":"Success","data":[]}"#;
    let api: ApiResponse = serde_json::from_str(success_response)?;
    match api {
        ApiResponse::Success { data } => println!("Got {} users", data.len()),
        ApiResponse::Error { code, message } => eprintln!("Error {}: {}", code, message),
    }

    // Validate after deserialization
    if user.email.is_empty() {
        return Err("email must not be empty".into());
    }

    Ok(())
}
