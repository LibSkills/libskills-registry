use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // TCP echo server
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    println!("Listening on 127.0.0.1:8080");

    loop {
        let (mut socket, addr) = listener.accept().await?;
        println!("Accepted connection from {}", addr);

        // Spawn a task per connection
        tokio::spawn(async move {
            let mut buf = [0u8; 1024];
            loop {
                match socket.read(&mut buf).await {
                    Ok(0) => { println!("Connection closed"); return; }
                    Ok(n) => {
                        if socket.write_all(&buf[..n]).await.is_err() {
                            return;
                        }
                    }
                    Err(_) => return,
                }
            }
        });
    }
}
