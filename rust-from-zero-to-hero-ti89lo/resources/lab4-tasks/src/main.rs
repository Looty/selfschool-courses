use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use std::path::PathBuf;
use tasks::Store;

/// A small command-line task tracker.
#[derive(Parser)]
#[command(version, about)]
struct Cli {
    /// Where the tasks are stored
    #[arg(short, long, default_value = "tasks.json")]
    file: PathBuf,

    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Add a task
    Add { title: String },
    /// Mark a task as done
    Done { id: u32 },
    /// Delete a task
    Remove { id: u32 },
    /// List tasks
    List {
        /// Also show finished tasks
        #[arg(short, long)]
        all: bool,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let mut store = Store::load(&cli.file)
        .with_context(|| format!("failed to load {}", cli.file.display()))?;

    match cli.command {
        Command::Add { title } => {
            let task = store.add(&title)?;
            println!("added #{}: {}", task.id, task.title);
        }
        Command::Done { id } => {
            let task = store.complete(id)?;
            println!("done #{}: {}", task.id, task.title);
        }
        Command::Remove { id } => {
            let task = store.remove(id)?;
            println!("removed #{}: {}", task.id, task.title);
        }
        Command::List { all } => {
            for t in store.list(all) {
                println!("[{}] #{} {}", if t.done { "x" } else { " " }, t.id, t.title);
            }
            return Ok(()); // nothing changed, no need to save
        }
    }

    store.save(&cli.file).with_context(|| format!("failed to save {}", cli.file.display()))?;
    Ok(())
}
